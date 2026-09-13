# Run after analyse.py; reuses the exact source preparation without rerunning its models.
from pathlib import Path
import json
exec(Path(__file__).with_name('analyse.py').read_text().split("result={'counts'")[0])
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import roc_auc_score
cat=['product_purchased','ticket_type','ticket_subject','ticket_priority','ticket_channel','industry','region','company_size','plan_type'];num=[k+s for k in metrics for s in ['_baseline','_recent','_change']]
cv=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=123);rows=[]
for fold,(ai,bi) in enumerate(cv.split(r,r.low_csat,r.customer_id)):
 a,b=r.iloc[ai],r.iloc[bi]
 for name,cats,nums in [('context',cat,[]),('usage',[],num),('usage_no_active_days',[],[x for x in num if not x.startswith('active_days')]),('combined',cat,num),('decline_rule',[],[])]:
  if name=='decline_rule':scores=-b.sessions_change.to_numpy()
  else:
   model=make_pipeline(ColumnTransformer([('cat',OneHotEncoder(handle_unknown='ignore'),cats),('num',StandardScaler(),nums)]),LogisticRegression(max_iter=2000));model.fit(a[cats+nums],a.low_csat);scores=model.predict_proba(b[cats+nums])[:,1]
  k=int(np.ceil(.2*len(b)));ix=np.argsort(-scores,kind='stable')[:k];rows.append({'fold':fold,'model':name,'auc':roc_auc_score(b.low_csat,scores),'precision20':b.low_csat.iloc[ix].mean(),'n':len(b)})
v=pd.DataFrame(rows);v.to_csv(out/'validation_folds.csv',index=False)
# The alternate period excludes May, which overlaps the first support timestamps.
r['earlier_change']=(r['sessions_2023-03']+r['sessions_2023-04'])/(r['sessions_2023-01']+r['sessions_2023-02'])-1
alternate=r.groupby(r.earlier_change.le(-.2)).low_csat.agg(['size','sum','mean']);print('CV',v.groupby('model')[['auc','precision20']].agg(['mean','std']).to_string());print('EARLIER PERIOD',alternate.to_string());print('BY PRODUCT',r.groupby(['product_purchased','decline20']).low_csat.agg(['size','mean']).to_string())
# Pooled difference CI with customer bootstrap for repeated-ticket dependence.
rng=np.random.default_rng(17);g=r.groupby(['customer_id','decline20']).low_csat.agg(['sum','size']).unstack(fill_value=0).reindex(columns=pd.MultiIndex.from_product([['sum','size'],[False,True]]),fill_value=0).to_numpy();diff=[]
for _ in range(2000):
 total=g[rng.integers(0,len(g),len(g))].sum(axis=0);diff.append(total[1]/total[3]-total[0]/total[2])
extra={'cv':v.groupby('model')[['auc','precision20']].agg(['mean','std']).to_json(),'earlier_period':alternate.reset_index().to_dict('records'),'difference_cluster_bootstrap_95ci':np.quantile(diff,[.025,.975]).tolist(),'by_product':r.groupby(['product_purchased','decline20']).low_csat.agg(['size','mean']).reset_index().to_dict('records')};(out/'validation.json').write_text(json.dumps(extra,indent=2));print('DIFFERENCE CI',extra['difference_cluster_bootstrap_95ci'])
