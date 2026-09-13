"""Run steps in dependency order. Stops immediately if a stage fails."""
import argparse
from pathlib import Path
from settings import ROOT
from common import save_json
from datetime import datetime,timezone
from clean_data import run as clean
from merge_data import run as merge
from explore_data import run as explore
from visualize_data import run as visualize

def main():
 p=argparse.ArgumentParser();p.add_argument('--raw-dir',type=Path,default=ROOT/'data/raw');p.add_argument('--output-dir',type=Path,default=ROOT/'outputs');a=p.parse_args()
 report=a.output_dir/'reports/run_status.json'
 save_json(report,{'status':'running','started_utc':datetime.now(timezone.utc).isoformat()})
 try:
  clean(a.raw_dir,a.output_dir);merge(a.output_dir);explore(a.output_dir);visualize(a.output_dir)
 except Exception as error:
  save_json(report,{'status':'failed','error':str(error),'note':'Do not use outputs left over from a prior run.'});raise
 save_json(report,{'status':'succeeded','completed_utc':datetime.now(timezone.utc).isoformat()})
if __name__=='__main__':main()
