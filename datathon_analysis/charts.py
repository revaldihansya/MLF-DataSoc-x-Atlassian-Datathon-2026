from pathlib import Path
import sys,json
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
p=Path(sys.argv[1] if len(sys.argv)>1 else 'output/datathon_analysis');r=json.loads((p/'results.json').read_text());plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','savefig.facecolor':'white'})
fig,ax=plt.subplots(figsize=(10,6));groups=[r['focal']['False'],r['focal']['True']];vals=np.array([x['rate'] for x in groups])*100;low=np.array([x['ci'][0] for x in groups])*100;high=np.array([x['ci'][1] for x in groups])*100
ax.bar(['Other session changes','Sessions down at least 20%'],vals,color=['#8293AC','#176BCA'],width=.55,yerr=[vals-low,high-vals],capsize=6);ax.set_ylim(0,65);ax.yaxis.set_major_formatter(PercentFormatter());ax.set_ylabel('Tickets with CSAT 1 or 2');ax.set_title('Declining usage is associated with lower satisfaction',pad=22)
for i,(v,g) in enumerate(zip(vals,groups)):ax.text(i,v+7,f'{v:.1f}%\nn = {g["n"]:,}',ha='center',fontweight='bold')
fig.text(.08,.025,'Source: supplied synthetic CSVs. Jan-Feb vs Apr-May 2023 sessions.\nRated tickets only; 95% Wilson intervals. Association does not establish causation.',fontsize=10,color='#4A5568');fig.subplots_adjust(bottom=.19,top=.86,left=.1,right=.97);fig.savefig(p/'01_usage_and_satisfaction.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,5.5));counts=[2769,5700];ax.barh(['Rated / closed','Unrated / open or pending'],counts,color=['#176BCA','#8293AC'],height=.5);ax.set_xlim(0,7000);ax.set_xlabel('Tickets');ax.set_title('67.3% of supplied tickets have no satisfaction score',pad=20)
for i,v in enumerate(counts):ax.text(v+90,i,f'{v:,} ({v/8469:.1%})',va='center',fontweight='bold')
ax.invert_yaxis();fig.text(.08,.025,'Source: supplied customer_support_tickets.csv; 8,469 synthetic tickets.\nMissing satisfaction is unknown, not evidence of a negative experience.',fontsize=10,color='#4A5568');fig.subplots_adjust(left=.28,bottom=.2,top=.85,right=.96);fig.savefig(p/'02_feedback_coverage.png',dpi=180);plt.close(fig)
f=pd.read_csv(p/'validation_folds.csv');z=f.groupby('model').auc.mean();keys=['context','combined','usage','usage_no_active_days','decline_rule'];labels=['Ticket/context model','Combined model','Usage model','Usage model, excluding active days','Simple usage-decline ranking'];fig,ax=plt.subplots(figsize=(10,6));v=[z[x] for x in keys];ax.barh(labels,v,color=['#8293AC']*4+['#176BCA'],height=.55);ax.set_xlim(0,1);ax.axvline(.5,color='#596579',linestyle='--',linewidth=1);ax.set_xlabel('Mean ROC AUC across five customer-separated folds');ax.set_title('AI scoring did not improve on a simple baseline',pad=20);ax.invert_yaxis()
for i,x in enumerate(v):ax.text(x+.015,i,f'{x:.3f}',va='center',fontweight='bold')
fig.text(.06,.025,'Source: supplied synthetic data; 2,769 rated tickets. AUC 0.5 = chance, 1.0 = perfect.\nExploratory retrospective evaluation. Differences do not establish superiority.',fontsize=10,color='#4A5568');fig.subplots_adjust(left=.37,right=.97,bottom=.18,top=.86);fig.savefig(p/'03_model_comparison.png',dpi=180);plt.close(fig)
