"""Plot only computed report tables. No statistical decisions or row deletion.
Run: python visualize_data.py --output-dir outputs
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from settings import ROOT
from common import require_files

def run(output_dir=ROOT/'outputs'):
 out=Path(output_dir);r=out/'reports';dest=out/'figures';dest.mkdir(parents=True,exist_ok=True)
 require_files([r/name for name in ['product_comparison.csv','product_subject_outcomes.csv','data_quality_summary.csv']], 'Run explore_data.py first, using the same --output-dir.')
 p=pd.read_csv(r/'product_comparison.csv');plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold'})
 def save(fig,name,note):
  fig.text(.04,.025,note,fontsize=9,color='#465368');fig.subplots_adjust(bottom=.22,top=.84,left=.12,right=.96);fig.savefig(dest/name,dpi=170);plt.close(fig)
 fig,ax=plt.subplots(figsize=(9,5.5));v=p.low_csat_rate*100;ax.bar(p['product'],v,color='#2563AA',yerr=[v-p.wilson_lower*100,p.wilson_upper*100-v],capsize=4);ax.set_ylim(0,65);ax.yaxis.set_major_formatter(PercentFormatter());ax.set_title('Ticket-associated satisfaction by product')
 for i,row in p.iterrows():ax.text(i,row.wilson_upper*100+2,f'n={row.rated_tickets:,}',ha='center',fontsize=10)
 save(fig,'01_product_ticket_csat.png','CSAT 1-2 among rated tickets; 95% Wilson intervals (ticket-level approximation).\nSource: supplied synthetic data. This is not a direct product-satisfaction measure.')
 fig,ax=plt.subplots(figsize=(9,5.5));ax.bar(p['product'],p.refund_type_share*100,color='#2563AA');ax.set_ylim(0,35);ax.yaxis.set_major_formatter(PercentFormatter());ax.set_title('Refund requests within the supplied tickets\nShare by product')
 for i,row in p.iterrows():ax.text(i,row.refund_type_share*100+1,f'{row.refund_type_share:.1%}',ha='center')
 save(fig,'02_refund_ticket_mix.png','Definition: Ticket Type = Refund request / all supplied tickets for that product.\nSource: supplied synthetic data. Not completed refunds or a population-wide refund rate.')
 s=pd.read_csv(r/'product_subject_outcomes.csv');mat=s.pivot(index='ticket_subject',columns='product',values='low_csat_rate');n=s.pivot(index='ticket_subject',columns='product',values='rated_tickets').reindex_like(mat)
 fig,ax=plt.subplots(figsize=(10,9));im=ax.imshow(mat,vmin=0,vmax=1,cmap='Blues',aspect='auto');ax.set_xticks(range(len(mat.columns)),mat.columns);ax.set_yticks(range(len(mat.index)),mat.index);ax.set_title('Product and subject: low ticket satisfaction')
 for i in range(len(mat)):
  for j in range(len(mat.columns)):
   v=mat.iloc[i,j];count=n.iloc[i,j]
   if pd.notna(v):ax.text(j,i,f'{v:.0%}\n(n={count:.0f})',ha='center',va='center',fontsize=8,color='white' if v>.6 else '#162334')
 fig.colorbar(im,ax=ax,fraction=.03,format=PercentFormatter(1));fig.text(.04,.025,'CSAT 1-2 / rated tickets in each cell. Descriptive comparisons, not proven root causes.\nSource: supplied synthetic data. See association tests and small-group flags before selecting a story.',fontsize=9);fig.subplots_adjust(left=.29,bottom=.11,top=.92,right=.94);fig.savefig(dest/'03_product_subject_heatmap.png',dpi=170);plt.close(fig)
 q=pd.read_csv(r/'data_quality_summary.csv');q=q[~q.issue.eq('missing_outcome')].copy();q['label']=q['column'].str.replace('_',' ')+'\n'+q.issue.str.replace('_',' ');fig,ax=plt.subplots(figsize=(10,6));ax.barh(q.label,q.rows,color='#AF743C');ax.set_title('Data-quality flags requiring interpretation');ax.set_xlabel('Affected rows per issue (counts may overlap)');ax.invert_yaxis();fig.text(.04,.025,'Expected missing satisfaction is reported separately, not classified here as a data error.\nSource: supplied synthetic data. Statistical extremes are a separate review, not automatic exclusions.',fontsize=9);fig.subplots_adjust(left=.39,right=.96,bottom=.2,top=.85);fig.savefig(dest/'04_data_quality.png',dpi=170);plt.close(fig)
 print('Figures saved:',dest)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,default=ROOT/'outputs');a=p.parse_args();run(a.output_dir)
