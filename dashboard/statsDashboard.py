import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from datetime import datetime, date, timedelta
import seaborn as sns
import altair as alt
import argparse
import os
import base64
import sys

sys.path.insert(1, '/Users/javier/Desktop/Python/FHIR')
##
os.getcwd()
os.chdir(os.path.join(os.getcwd(), "FHIR", "dashboard"))
from utils.load_css import local_css, textFunc, statsTextFunc
from utils.dataQueryVis import dataQuery, Stat
from utils.dataTuples import codeDict, dateDict, codes, valueDict, patientDict
from utils.BGriskAssesment import BGRiskAssesment
alt.data_transformers.disable_max_rows()

a = Stat(date="2021-09-22")
a.__dir__()
a.getStatsDf(ndayList = [7,14,21])
a.PtDF['Patient/2023']['440404000'].keys()
a.ptAggReducedDF.keys()
a.getStatsDf(ndayList = [7,14,21])
len(a.PtDF.keys())
a.createReducedDF(7)
a.PtDF['Patient/2023']['440404000'].keys()
a.getStatsDf(ndayList = [7,14,21])
a.statDF['mean']

pd.to_numeric(a.statDF['mean'])
a.PtDF['Patient/2023'][codes['CGM']]['stats']
plt.scatter([pt for pt in a.PtDF.keys()], [a.PtDF[pt]['440404000']['stats']['mean'] for pt in a.PtDF.keys()])


plt.figure(figsize=(10,6), tight_layout=True)
tmpDF.columns
def plottest():
	# ax = sns.boxplot(data=tmpDF['7']["df"], x='Patients', y='CGM', palette='Set2', linewidth=2.5)
	# ax = sns.boxplot(data=tmpDF['14']["df"], x='Patients', y='CGM', palette='Set2', linewidth=2.5)
	ax = sns.violinplot(x='Patients', y='CGM', data=tmpDF['21']['df'], scale='width', inner='quartile')
	ax = sns.violinplot(x='Patients', y='CGM', data=tmpDF['7']['df'], scale='width', inner='quartile')
	ax.set(title='Boxplot', xlabel='', ylabel='Height (cm)')
	plt.show()

plottest()
ax = sns.boxplot(data=tmpDF['21']['df'], x='Patients', y='CGM', palette='Set2', linewidth=2.5)

sns.violinplot(x='Patients', y='CGM', data=tmpDF['21']['df'], scale='width', inner='quartile')
tmpDF = pd.concat([a.PtDF[pt][codes['CGM']]['dfReduced'] for pt in a.PtDF.keys()], ignore_index=True)
tmpDF['21']['stats']

tmpDF['7']['stats'][1].keys()
sns.scatterplot([[pt,pt,pt] for pt in a.PtDF.keys()], [[tmpDF[nDay]['stats'][pt]['mean'] for nDay in ['7','14','21']] for pt in a.PtDF.keys()])
plt.scatter([1,1,1], [tmpDF[nDay]['stats'][0]['mean'] for nDay in ['7','14','21']])
[tmpDF[str(nDay)]['stats'][0]['mean'] for nDay in [7,14,21]]

aa = pd.DataFrame.from_dict(tmpDF['7']['stats']['Patient/2023'], orient='index').T
aa['Patients'] = 'Patient/2023'
aa
pd.concat([aa, ], ignore_index=True)
next(iter(a.PtDF))
pd.DataFrame(columns = list(tmpDF['7']['stats']['Patient/2023'].keys()))



tmp = makeStatsDf()
tmp.columns
sns.catplot(x="Patients", y="GMI", hue="timeWindow", kind="swarm", data=a.tmp, s=15)
a.tmpDF.keys()
