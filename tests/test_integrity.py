"""Small tests for mistakes that would invalidate the analysis."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from common import low_csat,require_unique
from clean_data import clean_table,REQUIRED
from merge_data import build_usage_summary
from settings import USAGE_METRICS

class IntegrityTests(unittest.TestCase):
 def test_unknown_csat_is_not_a_negative_label(self):
  result=low_csat(pd.Series([1.,2.,3.,5.,np.nan]));self.assertEqual(result.iloc[:4].tolist(),[True,True,False,False]);self.assertTrue(pd.isna(result.iloc[4]))
 def test_duplicate_dimension_key_blocks_join(self):
  with self.assertRaises(ValueError):require_unique(pd.DataFrame({'customer_email':['a','a']}),['customer_email'],'test')
 def test_missing_dimension_key_blocks_join(self):
  with self.assertRaises(ValueError):require_unique(pd.DataFrame({'customer_id':['a',None]}),['customer_id'],'test')
 def usage(self):
  rows=[]
  for month,sessions in [('2023-01',20),('2023-02',20),('2023-04',12),('2023-05',12)]:
   rows.append({'customer_id':'X','product':'Jira','month':month,**{k:1 for k in USAGE_METRICS},'sessions':sessions})
  return pd.DataFrame(rows)
 def test_usage_change_uses_customer_product_window(self):
  x=build_usage_summary(self.usage());self.assertAlmostEqual(x.sessions_change.iloc[0],-.4)
 def test_missing_month_does_not_become_zero(self):
  x=build_usage_summary(self.usage().query("month != '2023-05'"));self.assertTrue(pd.isna(x.sessions_recent.iloc[0]));self.assertTrue(pd.isna(x.sessions_change.iloc[0]))
 def test_zero_baseline_does_not_become_infinite(self):
  u=self.usage();u.loc[u.month.isin(['2023-01','2023-02']),'sessions']=0;x=build_usage_summary(u);self.assertTrue(pd.isna(x.sessions_change.iloc[0]))
 def test_impossible_days_only_mask_affected_value(self):
  raw=pd.DataFrame({'Customer ID':['X'],'Product':['jira'],'Month':['2023-02'],'Active Days':['31'],'Sessions':['10'],'Product Actions':['20'],'Collaborators':['3'],'Integrations Used':['1']});before=raw.copy(deep=True)
  clean,_=clean_table(raw,'usage');pd.testing.assert_frame_equal(raw,before);self.assertTrue(pd.isna(clean.active_days.iloc[0]));self.assertEqual(clean.sessions.iloc[0],10);self.assertEqual(clean['product'].iloc[0],'Jira')
 def test_invalid_csat_is_masked_but_ticket_kept(self):
  row={column:'' for column in REQUIRED['tickets']};row.update(ticket_id='1',customer_satisfaction_rating='9',ticket_status='Closed')
  raw=pd.DataFrame([row]);clean,_=clean_table(raw,'tickets');self.assertEqual(len(clean),1);self.assertTrue(pd.isna(clean.customer_satisfaction_rating.iloc[0]))

if __name__=='__main__':unittest.main()
