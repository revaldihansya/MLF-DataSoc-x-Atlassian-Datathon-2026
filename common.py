"""Small shared utilities; no work runs on import."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd

def require_files(paths, hint):
 missing = [str(path) for path in paths if not Path(path).is_file()]
 if missing:
  raise FileNotFoundError('Missing required inputs:\n' + '\n'.join(missing) + '\n' + hint)

def save_json(path, value):
 Path(path).parent.mkdir(parents=True,exist_ok=True)
 Path(path).write_text(json.dumps(value,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)),encoding='utf-8')

def fingerprint(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def require_unique(df, keys, label):
 if df[keys].isna().any().any(): raise ValueError(f'{label}: missing key in {keys}; resolve before merging.')
 if df.duplicated(keys).any(): raise ValueError(f'{label}: duplicate key {keys}; resolve before merging; do not multiply rows.')

def low_csat(score):
 """Keep missing outcomes unknown instead of accidentally making them False."""
 return score.le(2).where(score.notna()).astype('boolean')

def wilson(k,n):
 if n==0:return (np.nan,np.nan)
 z=1.959963984540054;p=k/n;den=1+z*z/n
 mid=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
 return mid-half,mid+half

def read_processed(path):
 d=pd.read_csv(path)
 for c in d:
  if c.startswith('flag_') or c in ['low_csat','declining_sessions']:
   d[c]=d[c].map({True:True,False:False,'True':True,'False':False}).astype('boolean')
 return d
