"""Summarise clean usage, then LEFT JOIN without changing ticket counts.
Run clean_data.py first. Run: python merge_data.py --output-dir outputs
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from common import read_processed,require_unique,save_json,low_csat,require_files
from settings import ROOT,USAGE_METRICS,BASELINE_MONTHS,RECENT_MONTHS,EARLIER_MONTHS,DECLINE_THRESHOLD

def build_usage_summary(u):
 require_unique(u,['customer_id','product','month'],'usage summary input')
 keys=['customer_id','product'];summary=u.groupby(keys).agg(months_observed=('month','nunique')).reset_index()
 for window,months in [('baseline',BASELINE_MONTHS),('recent',RECENT_MONTHS),('earlier',EARLIER_MONTHS)]:
  part=u[u.month.isin(months)];group=part.groupby(keys)
  for metric in USAGE_METRICS:
   v=group[metric].agg(['mean','count']);v['mean']=v['mean'].where(v['count'].eq(len(months)))
   v=v.rename(columns={'mean':f'{metric}_{window}','count':f'{metric}_{window}_valid_months'}).reset_index();summary=summary.merge(v,on=keys,how='left',validate='one_to_one')
 for metric in USAGE_METRICS:
  base=summary[metric+'_baseline'];recent=summary[metric+'_recent'];summary[metric+'_change']=(recent/base.where(base.gt(0))-1)
  summary[metric+'_zero_baseline']=base.eq(0)&base.notna()
 summary['sessions_earlier_change']=summary.sessions_earlier/summary.sessions_baseline.where(summary.sessions_baseline.gt(0))-1
 return summary

def run(output_dir=ROOT/'outputs'):
 out=Path(output_dir);clean=out/'clean';processed=out/'processed';processed.mkdir(parents=True,exist_ok=True)
 require_files([clean/(name+'.csv') for name in ['customers','tickets','usage']], 'Run clean_data.py first, using the same --output-dir.')
 c=read_processed(clean/'customers.csv');t=read_processed(clean/'tickets.csv');u=read_processed(clean/'usage.csv')
 require_unique(c,['customer_email'],'customers');require_unique(t,['ticket_id'],'tickets');s=build_usage_summary(u)
 master=c[['customer_email','customer_id','customer_name','customer_age','customer_gender','plan_type','industry','region','company_size','account_created_date']]
 joined=t.merge(master,on='customer_email',how='left',suffixes=('_ticket','_master'),validate='many_to_one',indicator='customer_match')
 conflicts={}
 for col in ['customer_name','customer_age','customer_gender']:
  a,b=joined[col+'_ticket'],joined[col+'_master'];conflicts[col]=int((a.notna()&b.notna()&a.ne(b)).sum())
 joined=joined.rename(columns={'product_purchased':'product'});joined=joined.merge(s,on=['customer_id','product'],how='left',validate='many_to_one',indicator='usage_match')
 if len(joined)!=len(t):raise ValueError('Join changed ticket count.')
 joined['low_csat']=low_csat(joined.customer_satisfaction_rating)
 joined['declining_sessions']=joined.sessions_change.le(DECLINE_THRESHOLD).where(joined.sessions_change.notna()).astype('boolean')
 audit={'tickets_before':len(t),'tickets_after':len(joined),'unmatched_customers':int(joined.customer_match.ne('both').sum()),'unmatched_usage':int(joined.usage_match.ne('both').sum()),'demographic_conflicts':conflicts,'usage_customer_product_rows':len(s),'baseline_months':BASELINE_MONTHS,'recent_months':RECENT_MONTHS,'earlier_months':EARLIER_MONTHS,'time_interpretation':'Descriptive windows only; ticket creation timestamps absent. May overlaps earliest support timestamps.'}
 # Do not include personal names/email/age/gender or meaningless resolution prose in model-ready evidence.
 private=[x for x in joined if x.startswith(('customer_name','customer_age','customer_gender')) or x in ['customer_email','resolution']]
 joined=joined.drop(columns=private)
 joined.to_csv(processed/'analysis_tickets.csv',index=False);s.to_csv(processed/'usage_summary.csv',index=False)
 ticket_counts=joined.groupby(['customer_id','product']).size().rename('supplied_ticket_count').reset_index();cp=s.merge(ticket_counts,on=['customer_id','product'],how='left',validate='one_to_one');cp['supplied_ticket_count']=cp.supplied_ticket_count.fillna(0).astype(int);cp.to_csv(processed/'analysis_customer_product.csv',index=False)
 save_json(out/'reports/join_audit.json',audit);print('Join audit:',audit);return joined

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,default=ROOT/'outputs');a=p.parse_args();run(a.output_dir)
