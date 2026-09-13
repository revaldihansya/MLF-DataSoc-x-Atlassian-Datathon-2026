from pathlib import Path
import json,sys
import pandas as pd,numpy as np
from scipy.stats import chi2_contingency, mannwhitneyu
from sklearn.model_selection import GroupShuffleSplit
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss
root=Path(sys.argv[1] if len(sys.argv)>1 else 'tmp/data');out=Path(sys.argv[2] if len(sys.argv)>2 else 'output/datathon_analysis');out.mkdir(exist_ok=True,parents=True)
def read(n):
 d=pd.read_csv(root/(n+'.csv'));d.columns=d.columns.str.lower().str.replace(' ','_');return d
c,t,u=read('customers'),read('customer_support_tickets'),read('product_usage')
m=t.merge(c[['customer_email','customer_id','industry','region','company_size','plan_type']],on='customer_email',validate='many_to_one')
metrics=['active_days','sessions','product_actions','collaborators','integrations_used'];p=u.pivot(index=['customer_id','product'],columns='month',values=metrics);p.columns=['_'.join(x) for x in p.columns]
for k in metrics:
 p[k+'_baseline']=p[[k+'_2023-01',k+'_2023-02']].mean(axis=1);p[k+'_recent']=p[[k+'_2023-04',k+'_2023-05']].mean(axis=1);p[k+'_change']=p[k+'_recent']/p[k+'_baseline'].replace(0,np.nan)-1
p=p.fillna(0);m=m.merge(p,left_on=['customer_id','product_purchased'],right_index=True,validate='many_to_one');m['low_csat']=m.customer_satisfaction_rating.le(2);m['decline20']=m.sessions_change.le(-.2);m['decline30']=m.sessions_change.le(-.3)
r=m[m.customer_satisfaction_rating.notna()].copy();r['low_csat']=r.low_csat.astype(int)
result={'counts':{'customers':len(c),'tickets':len(t),'usage_rows':len(u),'customer_products':len(p),'rated':len(r),'low_csat':int(r.low_csat.sum()),'unique_rated_customers':r.customer_id.nunique()},'dates':{}}
for col in ['first_response_time','time_to_resolution','date_of_purchase']:
 dt=pd.to_datetime(t[col],dayfirst=True);result['dates'][col]={'min':str(dt.min()),'max':str(dt.max())}
fr=pd.to_datetime(t.first_response_time,dayfirst=True);tr=pd.to_datetime(t.time_to_resolution,dayfirst=True);delta=(tr-fr).dt.total_seconds()/3600;result['timing']={'valid_pairs':int(delta.notna().sum()),'negative_pairs':int(delta.lt(0).sum())}
result['usage_invalid_active_days']=int((u.active_days>pd.to_datetime(u.month).dt.days_in_month).sum())
result['segments']={}
for col in ['product_purchased','ticket_type','ticket_subject','ticket_priority','ticket_channel','plan_type','industry','region','company_size','decline20','decline30']:
 tab=r.groupby(col).agg(n=('low_csat','size'),low=('low_csat','sum'),low_rate=('low_csat','mean'),mean_csat=('customer_satisfaction_rating','mean'));tab.to_csv(out/('segment_'+col+'.csv'));result['segments'][col]={'table':tab.reset_index().to_dict('records'),'p':chi2_contingency(pd.crosstab(r[col],r.low_csat))[1]}
result['usage_by_rating']=r.groupby('customer_satisfaction_rating')[['sessions_baseline','sessions_recent','sessions_change','active_days_recent','product_actions_recent','collaborators_recent','integrations_used_recent']].mean().reset_index().to_dict('records')
result['operational']={'unrated':int(m.customer_satisfaction_rating.isna().sum()),'unrated_decline20':int((m.customer_satisfaction_rating.isna()&m.decline20).sum()),'unrated_decline30':int((m.customer_satisfaction_rating.isna()&m.decline30).sum()),'unrated_decline20_customers':m.loc[m.customer_satisfaction_rating.isna()&m.decline20,'customer_id'].nunique()}
cat=['product_purchased','ticket_type','ticket_subject','ticket_priority','ticket_channel','industry','region','company_size','plan_type'];num=[k+s for k in metrics for s in ['_baseline','_recent','_change']]
train,test=next(GroupShuffleSplit(n_splits=1,test_size=.25,random_state=42).split(r,groups=r.customer_id));a,b=r.iloc[train],r.iloc[test];result['split']={'train':len(a),'test':len(b),'test_positive':int(b.low_csat.sum()),'test_prevalence':b.low_csat.mean(),'overlapping_customers':len(set(a.customer_id)&set(b.customer_id))};result['models']={}
for name,cats,nums,est in [('ticket_context',cat,[],LogisticRegression(max_iter=2000)),('usage',[],num,LogisticRegression(max_iter=2000)),('combined',cat,num,LogisticRegression(max_iter=2000)),('combined_rf',cat,num,RandomForestClassifier(n_estimators=250,min_samples_leaf=20,max_depth=8,random_state=42,n_jobs=-1))]:
 prep=ColumnTransformer([('cat',OneHotEncoder(handle_unknown='ignore'),cats),('num',StandardScaler(),nums)]);model=make_pipeline(prep,est);model.fit(a[cats+nums],a.low_csat);scores=model.predict_proba(b[cats+nums])[:,1];y=b.low_csat.to_numpy();k=int(np.ceil(.2*len(b)));ix=np.argsort(-scores,kind='stable')[:k];rng=np.random.default_rng(42);auc=[]
 for _ in range(1000):
  ids=rng.integers(0,len(y),len(y))
  if len(np.unique(y[ids]))==2:auc.append(roc_auc_score(y[ids],scores[ids]))
 result['models'][name]={'auc':roc_auc_score(y,scores),'auc_ci':np.quantile(auc,[.025,.975]).tolist(),'ap':average_precision_score(y,scores),'brier':brier_score_loss(y,scores),'top20_n':k,'top20_low':int(y[ix].sum()),'top20_precision':float(y[ix].mean()),'top20_recall':float(y[ix].sum()/y.sum())}
 if name=='combined':
  feat=model[0].get_feature_names_out();result['coefficients']=sorted(zip(feat,model[1].coef_[0]),key=lambda x:abs(x[1]),reverse=True)[:20]
# Simple prespecified queue baselines on the same test set.
result['baselines']={}
for name,scores in [('usage_decline',-b.sessions_change.to_numpy()),('low_recent_sessions',-b.sessions_recent.to_numpy()),('priority',b.ticket_priority.map({'Critical':4,'High':3,'Medium':2,'Low':1}).to_numpy())]:
 k=int(np.ceil(.2*len(b)));ix=np.argsort(-scores,kind='stable')[:k];result['baselines'][name]={'auc':roc_auc_score(b.low_csat,scores),'top20_n':k,'top20_low':int(b.low_csat.iloc[ix].sum()),'top20_precision':b.low_csat.iloc[ix].mean()}
# Confidence intervals for the focal descriptive pattern; Wilson intervals.
def proportion_confint(k,n,method=None):
 z=1.959963984540054;p=k/n;den=1+z*z/n;mid=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den;return mid-half,mid+half
result['focal']={}
for flag,g in r.groupby('decline20'):
 lo,hi=proportion_confint(g.low_csat.sum(),len(g),method='wilson');result['focal'][str(flag)]={'n':len(g),'low':int(g.low_csat.sum()),'rate':g.low_csat.mean(),'ci':[lo,hi]}
# Sensitivity to repeated customer emails: retain one ticket per customer (smallest ticket ID, not chronology).
s=r.sort_values('ticket_id').drop_duplicates('customer_id');result['deduplicated_focal']=s.groupby('decline20').low_csat.agg(['size','mean']).reset_index().to_dict('records')
result['decline_by_plan']=m[m.customer_satisfaction_rating.isna()&m.decline20].groupby('plan_type').size().to_dict()
# Anonymous audit table avoids exporting names and email addresses.
cols=['ticket_id','customer_id','product_purchased','ticket_status','ticket_priority','plan_type','customer_satisfaction_rating','sessions_baseline','sessions_recent','sessions_change','decline20'];m[cols].to_csv(out/'ticket_evidence.csv',index=False)
(out/'results.json').write_text(json.dumps(result,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)))
print(json.dumps({k:v for k,v in result.items() if k not in ['segments','coefficients']},indent=2));print('SEGMENT P VALUES',[(k,round(v['p'],6)) for k,v in result['segments'].items()]);print('COEFFICIENTS',result['coefficients'])
