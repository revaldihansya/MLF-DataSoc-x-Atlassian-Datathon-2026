"""Descriptive tables and exploratory association tests. No model training.
Run: python explore_data.py --output-dir outputs
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency,spearmanr,false_discovery_control
from common import read_processed,wilson,save_json,require_files
from settings import ROOT,CATEGORICAL_PREDICTORS,USAGE_METRICS,TECHNICAL_SUBJECTS,MIN_DISPLAY_N

def group_outcomes(d, columns):
 rows=[]
 for key,g in d.groupby(columns,dropna=False,observed=True):
  key=key if isinstance(key,tuple) else (key,);rated=g[g.customer_satisfaction_rating.notna()];n=len(rated);k=int(rated.low_csat.sum());lo,hi=wilson(k,n)
  rows.append(dict(zip(columns,key))|{'tickets':len(g),'rated_tickets':n,'rating_coverage':n/len(g),'low_csat_tickets':k,'low_csat_rate':k/n if n else np.nan,'wilson_lower':lo,'wilson_upper':hi,'small_rated_group':n<MIN_DISPLAY_N})
 return pd.DataFrame(rows)

def categorical_test(d, column, outcome='low_csat', family='csat'):
 x=d[[column,outcome]].dropna();tab=pd.crosstab(x[column],x[outcome]);base={'family':family,'variable':column,'outcome':outcome,'n':len(x),'method':'chi_square','effect_name':'cramers_v','effect':np.nan,'p_value':np.nan}
 if min(tab.shape)<2:return base|{'status':'insufficient variation'}
 chi,p,_,expected=chi2_contingency(tab,correction=False);effect=np.sqrt(chi/(tab.to_numpy().sum()*min(tab.shape[0]-1,tab.shape[1]-1)))
 # Conservative rule: do not automatically publish asymptotic p when any expected cell is <5.
 if expected.min()<5:return base|{'effect':effect,'status':'sparse expected cells; review exact/permutation alternative','min_expected':float(expected.min())}
 return base|{'effect':effect,'p_value':p,'status':'exploratory','min_expected':float(expected.min())}

def run(output_dir=ROOT/'outputs'):
 out=Path(output_dir);(out/'reports').mkdir(parents=True,exist_ok=True)
 require_files([out/'processed/analysis_tickets.csv',out/'processed/analysis_customer_product.csv',out/'clean/usage.csv',out/'reports/data_quality_issues.csv'], 'Run clean_data.py and merge_data.py first, using the same --output-dir.')
 out=Path(output_dir);reports=out/'reports';d=read_processed(out/'processed/analysis_tickets.csv');cp=read_processed(out/'processed/analysis_customer_product.csv');u=read_processed(out/'clean/usage.csv')
 product=group_outcomes(d,['product']);extras=[]
 for name,g in d.groupby('product'):
  extras.append({'product':name,'unique_ticket_customers':g.customer_id.nunique(),'refund_type_share':g.ticket_type.eq('Refund request').mean(),'refund_subject_share':g.ticket_subject.eq('Refund request').mean(),'cancellation_type_share':g.ticket_type.eq('Cancellation request').mean(),'technical_type_share':g.ticket_type.eq('Technical issue').mean(),'analyst_grouped_technical_subject_share':g.ticket_subject.isin(TECHNICAL_SUBJECTS).mean()})
 product=product.merge(pd.DataFrame(extras),on='product',validate='one_to_one')
 use=cp.groupby('product').agg(observed_customer_product_pairs=('customer_id','size'),median_sessions_baseline=('sessions_baseline','median'),median_sessions_recent=('sessions_recent','median'),median_within_customer_session_change=('sessions_change','median'),eligible_usage_pairs=('sessions_change','count'),pairs_without_supplied_tickets=('supplied_ticket_count',lambda s:int(s.eq(0).sum()))).reset_index()
 product=product.merge(use,on='product',validate='one_to_one');product['tickets_per_observed_customer_product']=product.tickets/product.observed_customer_product_pairs
 product.to_csv(reports/'product_comparison.csv',index=False)
 group_outcomes(d,['product','ticket_subject']).to_csv(reports/'product_subject_outcomes.csv',index=False)
 group_outcomes(d,['product','ticket_type']).to_csv(reports/'product_type_outcomes.csv',index=False)
 for c in CATEGORICAL_PREDICTORS:group_outcomes(d,[c]).to_csv(reports/('outcomes_by_'+c+'.csv'),index=False)
 group_outcomes(d,['declining_sessions']).to_csv(reports/'usage_decline_outcomes.csv',index=False)
 pd.crosstab(d.ticket_type,d.ticket_subject).to_csv(reports/'type_subject_crosstab.csv')
 pd.crosstab(d.ticket_status,d.customer_satisfaction_rating.isna()).rename(columns={False:'rated',True:'unrated'}).to_csv(reports/'rating_missingness_by_status.csv')
 u.groupby(['product','month']).agg(observed_pairs=('customer_id','size'),median_sessions=('sessions','median'),mean_sessions=('sessions','mean'),median_product_actions=('product_actions','median')).reset_index().to_csv(reports/'product_monthly_usage.csv',index=False)
 # The supplied product population is selected: no assumption that it includes non-ticketing customers.
 # Distinct analysis population for basic tests avoids repeated tickets per customer.
 rated=d[d.customer_satisfaction_rating.notna()&d.customer_id.notna()].copy();independent=rated.sort_values('ticket_id').drop_duplicates('customer_id')
 tests=[categorical_test(independent,c) for c in CATEGORICAL_PREDICTORS]
 numerical=[metric+'_'+window for metric in USAGE_METRICS for window in ['baseline','recent','change']]+['sessions_earlier_change']
 for c in numerical:
  x=independent[[c,'customer_satisfaction_rating']].dropna();row={'family':'csat','variable':c,'outcome':'customer_satisfaction_rating','n':len(x),'method':'spearman_rank','effect_name':'spearman_rho','effect':np.nan,'p_value':np.nan,'status':'insufficient variation'}
  if len(x)>2 and x[c].nunique()>1:
   result=spearmanr(x[c],x.customer_satisfaction_rating);row.update(effect=result.statistic,p_value=result.pvalue,status='exploratory')
  tests.append(row)
 for name,g in independent.groupby('product'):tests.append(categorical_test(g,'ticket_subject',family='within_product_subject_'+str(name)))
 all_one=d[d.customer_id.notna()].sort_values('ticket_id').drop_duplicates('customer_id').copy()
 for name,value in [('refund_type','Refund request'),('cancellation_type','Cancellation request')]:
  all_one[name]=all_one.ticket_type.eq(value);tests.append(categorical_test(all_one,'product',outcome=name,family='ticket_mix'))
 tests=pd.DataFrame(tests);valid=tests.p_value.notna()
 tests['p_adjusted_bh']=np.nan;tests['p_adjusted_by']=np.nan
 if valid.any():
  tests.loc[valid,'p_adjusted_bh']=false_discovery_control(tests.loc[valid,'p_value'].to_numpy(),method='bh')
  tests.loc[valid,'p_adjusted_by']=false_discovery_control(tests.loc[valid,'p_value'].to_numpy(),method='by')
 tests.to_csv(reports/'exploratory_association_tests.csv',index=False)
 # Review plausible extremes within products; never remove them automatically.
 extremes=[]
 for product_name,g in u.groupby('product'):
  for metric in USAGE_METRICS:
   x=g[metric].dropna();q1,q3=x.quantile([.25,.75]);iqr=q3-q1;lower,upper=q1-1.5*iqr,q3+1.5*iqr
   extremes.append({'product':product_name,'metric':metric,'nonmissing_rows':len(x),'iqr_lower':lower,'iqr_upper':upper,'outside_iqr_fences':int(((x<lower)|(x>upper)).sum()),'action':'review only; values retained'})
 pd.DataFrame(extremes).to_csv(reports/'statistical_extremes.csv',index=False)
 quality=pd.read_csv(reports/'data_quality_issues.csv');quality.groupby(['table','column','issue','action']).size().rename('rows').reset_index().to_csv(reports/'data_quality_summary.csv',index=False)
 save_json(reports/'analysis_notes.json',{'rated_ticket_rows':len(rated),'one_rated_ticket_per_customer_for_tests':len(independent),'selection_rule':'smallest ticket_id for reproducibility; NOT chronological','tests_with_p':int(valid.sum()),'multiplicity':'BH and BY across ALL finite p-values in this run, including within-product and ticket-mix tests. BY accommodates arbitrary dependence. Exploratory, not causal.','intervals':'Wilson intervals in full ticket descriptive tables approximate repeated tickets as independent. Use customer cluster bootstrap for any selected headline.','limitations':['Synthetic dataset','CSAT concerns a support interaction and does not isolate product satisfaction','No creation date, reliable support durations, refunds completed, direct feature exposure or verified full product population','No aggregate ticket rate per calendar month can be established','Product usage comparisons use one customer-product row, not duplicated ticket rows','Lowest-ID selection changes the estimand; use customer-cluster models for deeper confirmation','Missing CSAT remains unknown; no imputation','Current usage windows are descriptive, not guaranteed pre-ticket inputs']})
 print(product[['product','tickets','rated_tickets','low_csat_rate','refund_type_share','median_within_customer_session_change']].to_string(index=False));return product

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,default=ROOT/'outputs');a=p.parse_args();run(a.output_dir)
