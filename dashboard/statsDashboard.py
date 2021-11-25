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
os.chdir(os.path.join(os.getcwd(), "FHIR"))
from utils.load_css import local_css, textFunc, statsTextFunc
from utils.dataQueryVis import dataQuery, Stat
from utils.dataTuples import codeDict, dateDict, codes, valueDict, patientDict
from utils.BGriskAssesment import BGRiskAssesment
alt.data_transformers.disable_max_rows()

a = Stat(date="2021-09-22")


class Stat(dataQuery):
	def __init__(self, date='2021-09-10', ptId=0, dateStart=0, dateEnd=0, thrsUL=55, thrsBR=80, thrsAR=200):
		super(Stat, self).__init__(date=date, ptId=ptId, dateStart=dateStart, dateEnd=dateEnd, thrsUL=thrsUL, thrsBR=thrsBR, thrsAR=thrsAR)

	def createReducedDF(self, numdays):
		for pt in self.PtDF.keys():
			for code in self.PtDF[pt].keys():
				try:
					initime = self.PtDF[pt][code]['df']['Dates'].max() - timedelta(days=numdays)
					self.PtDF[pt][code]['dfReduced'] = self.PtDF[pt][code]['df'][self.PtDF[pt][code]['df']['Dates'] > initime]
				except:
					pass
			try:
				self.PtDF[pt][codes['CGM']]['dfReduced'] = self.PtDF[pt][codes['CGM']]['dfReduced'].rename({valueDict[codes['CGM']] : 'CGM', patientDict[codes['CGM']] : 'Patients'}, axis=1)
				self.PtDF[pt][codes['CGM']]['dfReduced']['CGM (mmol/L)'] = self.PtDF[pt][codes['CGM']]['dfReduced']['CGM']/18.0
				for code in codes.keys():
					self.PtDF[pt][codes[code]]['dfReduced'] = self.PtDF[pt][codes[code]]['dfReduced'].rename({valueDict[codes[code]] : code, patientDict[codes[code]] : 'Patients'}, axis=1)

			except:
				pass

	def addStats(self, thrsUL=55, thrsBR=80, thrsAR=200):
		for pt in self.PtDF.keys():
			self.PtDF[pt][codes['CGM']]['stats'] ={
				'units' : "mg/dL",
				'mean' : str(round(np.mean(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM']),2)),
				'median' : str(np.median(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])),
				'min' : str(np.min(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])),
				'max' : str(np.max(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])),
				'var' : str(round(np.var(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM']),2)),
				'std' : str(round(np.std(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM']),2)),
				'sum' : str(np.sum(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])),
				'q25' : str(np.percentile(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'], 25)),
				'q50' : str(np.percentile(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'], 50)),
				'q75' : str(np.percentile(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'], 75)),
				'utilizationPerc' : str(round(len(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])/( ( self.getDate(str(self.PtDF[pt][codes['CGM']]['dfReduced']['Dates'].iloc[-1])) - self.getDate(str(self.PtDF[pt][codes['CGM']]['dfReduced']['Dates'].iloc[0]))).total_seconds()/60 * 1/5 + 1 ) * 100, 2)),
				'hypoRisk' : self.BGRiskAssesment.LBGRisk(),
				'LowBGIndex' : str(round(self.BGRiskAssesment.LBGI,3)),
				'HighBGIndex' : str(round(self.BGRiskAssesment.HBGI,3)),
				'nDays' : str(int(np.floor( (self.getDate(str(self.PtDF[pt][codes['CGM']]['dfReduced']['Dates'].iloc[-1])) - self.getDate(str(self.PtDF[pt][codes['CGM']]['dfReduced']['Dates'].iloc[0]))).total_seconds()/3600 * 1/24 + 1 ))),
				'nValues' : str(len(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])),
				'nUrgentLow' : str(sum(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] < thrsUL)),
				'nBelowRange' : str(sum((self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] >= thrsUL) & (self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] < thrsBR))),
				'nInRange' : str(sum((self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] >= thrsBR) & (self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] < thrsAR))),
				'nAboveRange' : str(sum(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] >= thrsAR)),
				'PerUrgentLow' : str(round(sum(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] < thrsUL)/len(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])*100,2)),
				'PerBelowRange' : str(round(sum((self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] >= thrsUL) & (self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] < thrsBR))/len(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])*100,2)),
				'PerInRange' : str(round(sum((self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] >= thrsBR) & (self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] < thrsAR))/len(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])*100,2)),
				'PerAboveRange' : str(round(sum(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] >= thrsAR)/len(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])*100,2)),
				'CoeffVariation' : str(round(np.std(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])/np.mean(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM']),2)),
				'GMI' : str(round(np.mean(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM']) * 0.02392 + 3.31, 2)),
				}
			self.PtDF[pt][codes['CGM']]['stats2'] ={
				'units' : "mmol/L",
				'mean' : str(round(np.mean(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM (mmol/L)']),2)),
				'median' : str(round(np.median(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM (mmol/L)']),3)),
				'min' : str(round(np.min(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM (mmol/L)']),2)),
				'max' : str(round(np.max(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM (mmol/L)']),2)),
				'var' : str(round(np.var(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM (mmol/L)']),2)),
				'std' : str(round(np.std(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM (mmol/L)']),2)),
				'sum' : str(round(np.sum(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM (mmol/L)']),2)),
				'q25' : str(round(np.percentile(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM (mmol/L)'], 25),2)),
				'q50' : str(round(np.percentile(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM (mmol/L)'], 50),2)),
				'q75' : str(round(np.percentile(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM (mmol/L)'], 75),2)),
				'utilizationPerc' : str(round(len(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])/( ( self.getDate(str(self.PtDF[pt][codes['CGM']]['dfReduced']['Dates'].iloc[-1])) - self.getDate(str(self.PtDF[pt][codes['CGM']]['dfReduced']['Dates'].iloc[0]))).total_seconds()/60 * 1/5 + 1 )*100, 2)),
				'hypoRisk' : self.BGRiskAssesment.LBGRisk(),
				'LowBGIndex' : str(round(self.BGRiskAssesment.LBGI,3)),
				'HighBGIndex' : str(round(self.BGRiskAssesment.HBGI,3)),
				'nDays' : str(int(np.floor( (self.getDate(str(self.PtDF[pt][codes['CGM']]['dfReduced']['Dates'].iloc[-1])) - self.getDate(str(self.PtDF[pt][codes['CGM']]['dfReduced']['Dates'].iloc[0]))).total_seconds()/3600 * 1/24 + 1 ))),
				'nValues' : str(len(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])),
				'nUrgentLow' : str(sum(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] < thrsUL)),
				'nBelowRange' : str(sum((self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] >= thrsUL) & (self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] < thrsBR))),
				'nInRange' : str(sum((self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] >= thrsBR) & (self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] < thrsAR))),
				'nAboveRange' : str(sum(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] >= thrsAR)),
				'PerUrgentLow' : str(round(sum(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] < thrsUL)/len(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])*100,2)),
				'PerBelowRange' : str(round(sum((self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] >= thrsUL) & (self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] < thrsBR))/len(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])*100,2)),
				'PerInRange' : str(round(sum((self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] >= thrsBR) & (self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] < thrsAR))/len(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])*100,2)),
				'PerAboveRange' : str(round(sum(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'] >= thrsAR)/len(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])*100,2)),
				'CoeffVariation' : str(round(np.std(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM'])/np.mean(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM']),2)),
				'GMI' : str(round(np.mean(self.PtDF[pt][codes['CGM']]['dfReduced']['CGM']) * 0.02392 + 3.31, 2)),
				}

	def genTmpDf(self, ndayList = [7,14,21]):
		df = {}
		for nDays in ndayList:
			self.createReducedDF(nDays)
			self.addStats()
			df[str(nDays)] = {"df" : pd.concat([self.PtDF[pt][codes['CGM']]['dfReduced'] for pt in self.PtDF.keys()], ignore_index=True)}
			# , "stats" : [{pt : self.PtDF[pt][codes['CGM']]['stats']} for pt in self.PtDF.keys()]}
			df[str(nDays)]['stats'] = {}
			for pt in self.PtDF.keys():
				df[str(nDays)]['stats'][pt] = self.PtDF[pt][codes['CGM']]['stats']
		return df

	def makeStatsDf(self, tmpDF):
		nDays = next(iter(tmpDF))
		pt = next(iter(tmpDF[nDays]['stats']))
		statsDF = pd.DataFrame(columns = list(tmpDF[nDays]['stats'][pt].keys()))
		statsDF['Patients'] = []
		statsDF['timeWindow'] = []
		for nDay in tmpDF.keys():
			for pt in tmpDF[nDay]['stats'].keys():

				aa = pd.DataFrame.from_dict(tmpDF[nDay]['stats'][pt], orient='index').T
				aa['Patients'] = pt
				aa['timeWindow'] = nDay

				statsDF = pd.concat([statsDF, aa])
				# statsDF.append(aa)
		return statsDF

	def getStatsDf(self, ndayList = [7,14,21]):
		self.tmpDF = self.genTmpDf(ndayList)
		self.tmp = self.makeStatsDf(self.tmpDF)


a.createReducedDF(7)
a.PtDF['Patient/2023']['440404000'].keys()
a.getStatsDf(ndayList = [7,14,21])
a.tmp
a.tmpDF.keys()
# reducedDF(5)
# a.PtDF
# str(aa)
# def genTmpDf(ndayList = [7,14,21]):
# 	df = {}
# 	for nDays in ndayList:
# 		reducedDF(nDays)
# 		getStats()
# 		df[str(nDays)] = {"df" : pd.concat([a.PtDF[pt][codes['CGM']]['dfReduced'] for pt in a.PtDF.keys()], ignore_index=True)}
# 		# , "stats" : [{pt : a.PtDF[pt][codes['CGM']]['stats']} for pt in a.PtDF.keys()]}
# 		df[str(nDays)]['stats'] = {}
# 		for pt in a.PtDF.keys():
# 			df[str(nDays)]['stats'][pt] = a.PtDF[pt][codes['CGM']]['stats']
# 	return df
# tmpDF = genTmpDf()
# codes
# valueDict
# a.PtDF.keys()
# a.PtDF['Patient/405878']['440404000'].keys()
# a.PtDF['Patient/2023']['440404000']['dfReduced']
# a.PtDF['Patient/2023'][codes['CarbIntake']]['dfReduced'].columns
# a.PtDF['Patient/2023']['440404000']['stats']
getStats()

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

def makeStatsDf():
	nDays = next(iter(tmpDF))
	pt = next(iter(tmpDF[nDays]['stats']))
	statsDF = pd.DataFrame(columns = list(tmpDF[nDays]['stats'][pt].keys()))
	statsDF['Patients'] = []
	statsDF['timeWindow'] = []
	for nDay in tmpDF.keys():
		for pt in tmpDF[nDay]['stats'].keys():

			aa = pd.DataFrame.from_dict(tmpDF[nDay]['stats'][pt], orient='index').T
			aa['Patients'] = pt
			aa['timeWindow'] = nDay

			statsDF = pd.concat([statsDF, aa])
			# statsDF.append(aa)
	return statsDF

tmp = makeStatsDf()
tmp.columns
sns.catplot(x="Patients", y="GMI", hue="timeWindow", kind="swarm", data=a.tmp, s=15)
