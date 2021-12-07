import pandas as pd
import os
from datetime import datetime, date, timedelta
import numpy as np
import json
import pytz
import sys
utc=pytz.UTC

from pathlib import Path
sys.path.insert(1, '/app/fhir/utils')
# sys.path.insert(1, os.path.join(Path(os.getcwd()).parent.absolute(), 'utils'))
# path = Path("/here/your/path/file/")
# print(path.parent.absolute())
# from utils.BGriskAssesment import BGRiskAssesment
# from utils.dataTuples import codeDict, dateDict, codes, valueDict, patientDict
from BGriskAssesment import BGRiskAssesment
from dataTuples import codeDict, dateDict, codes, valueDict, patientDict

class dataQuery(object):
	def __init__(self, date='2021-09-10', ptId=0, dateStart=0, dateEnd=0, thrsUL=55, thrsBR=80, thrsAR=200):
		# parentDir = Path(os.getcwd()).parent.absolute()
		parentDir = os.getcwd() + "/fhir"
		# self.metadata = self.loadJSON(os.path.join(os.getcwd(), 'Complete-' + date), 'Metadata.json')
		self.metadata = self.loadJSON(os.path.join(parentDir, 'Complete-' + date), 'Metadata.json')
		# self.dataDict = self.loadJSON(os.path.join(os.getcwd(), 'Complete-' + date), 'Data.json')
		self.dataDict = self.loadJSON(os.path.join(parentDir, 'Complete-' + date), 'Data.json')

		# fileList = os.listdir(os.path.join(os.getcwd(), f'Complete-{date}'))
		fileList = os.listdir(os.path.join(parentDir, f'Complete-{date}'))
		fLBool = [file.split(".")[1] == "csv" for file in fileList ]
		resList = [ file.split(".")[0] for i,file in enumerate(fileList) if fLBool[i] == True ]
		self.dfResDict = {}
		for key in resList:
			# self.dfResDict[key] = pd.read_csv(os.path.join(os.getcwd(), 'Complete-' + date, f'{key}.csv'))
			self.dfResDict[key] = pd.read_csv(os.path.join(parentDir, 'Complete-' + date, f'{key}.csv'))
			try:
				self.dfResDict[key]['Dates'] = self.dfResDict[key].apply(lambda x : self.getDate(str(x[dateDict[key]])), axis=1)
			except:
				pass

		self.createCodeDF()

		# self.ObsDF['Dates'] = self.ObsDF.apply(lambda x : self.getDate(str(x['root-effectiveDateTime'])), axis=1)
		self.createPtDF()

		self.getWindow(ptId, dateStart, dateEnd)
		self.BGRiskAssesment = BGRiskAssesment(self.reducedDF[codes['CGM']]['df']['CGM'])

	def saveJSON(self, obj, path, filename='FHIRdata.json'):
		dictJSON = json.dumps(obj)
		f = open(os.path.join(path, filename),"w")
		f.write(dictJSON)
		f.close()

	def loadJSON(self, path, file):
		with open(os.path.join(path, file), 'r') as h:
			js = json.load(h)
		return js

	def getDate(self, x):
		try:
			try:
				return datetime.fromisoformat(x[:-1])
			except:
				return datetime.fromisoformat(x[:])
		except:
			return x

	def createCodeDF(self):
		self.dfCodeDict = {}
		for k in self.metadata['Codes'].keys():
			for key in self.metadata['Codes'][k].keys():
				self.dfCodeDict[key] = { 'display' : self.metadata['Codes'][k][key]['display'], 'df' : self.dfResDict[k][self.dfResDict[k][codeDict[k]].astype(str) == key]}

	def createPtDF(self):
		self.PtDF = {}
		for pt in self.metadata['Patients']:
			self.PtDF[pt] = {}
			for code in self.dfCodeDict.keys():
				temp = self.dfCodeDict[code]['df'][self.dfCodeDict[code]['df']['root-subject-reference'] == pt]
				# codes = np.unique(temp[codeDict[key]]).tolist()
				# for code in codes:
				self.PtDF[pt][code] = {'df' : temp, 'display' : self.dfCodeDict[code]['display']}

	def getWindow(self, ptId=0, dateStart=0, dateEnd=0):
		if ptId == 0:
			ptId = 'Patient/405878'
			# ptId = next(iter(self.PtDF))
		# print(ptId)

		self.reducedDF = {}
		for key in self.PtDF[ptId].keys():
			# print(key)
			if dateStart == 0:
				q2 = [True for i in range(len(self.PtDF[ptId][key]['df'][valueDict[key]]))]#)[0]
			else:
				q2 = (self.PtDF[ptId][key]['df']['Dates'].astype(object) >= self.getDate(dateStart).replace(tzinfo=utc)).tolist()
			if dateEnd == 0:
				q3 = [True for i in range(len(self.PtDF[ptId][key]['df'][valueDict[key]]))]#)[0]
			else:
				q3 = (self.PtDF[ptId][key]['df']['Dates'].astype(object) <= self.getDate(dateEnd).replace(tzinfo=utc)).tolist()
			try:
				self.reducedDF[key] = {'display' : self.PtDF[ptId][key]['display'], "df" : self.PtDF[ptId][key]['df'][[a and b for (a, b) in zip(q2, q3)]]}
			except:
				# print(f'No {key} in this time window')
				pass

		self.reducedDF[codes['CGM']]['df'] = self.reducedDF[codes['CGM']]['df'].rename({valueDict[codes['CGM']] : 'CGM', patientDict[codes['CGM']] : 'Patients'}, axis=1)
		self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)'] = self.reducedDF[codes['CGM']]['df']['CGM']/18.0

		for code in codes.keys():
			self.reducedDF[codes[code]]['df'] = self.reducedDF[codes[code]]['df'].rename({valueDict[codes[code]] : code, patientDict[codes[code]] : 'Patients'}, axis=1)

		# self.reducedDF = self.PtDF[ptId][codes['CGM']]['df'][q2 and q3]
		# self.reducedDF = self.reducedDF.rename({'root-valueQuantity-value' : 'CGM', 'root-subject-reference' : 'Patients'}, axis=1)
		# self.reducedDF['CGM (mmol/L)'] = self.reducedDF['CGM']/18.0
		# return self.PtDF[ptId][codes['CGM']]['df'][q2 and q3]

	def getWindow3(self, ptId=0, dateStart=0, dateEnd=0):
		if ptId == 0:
			ptId = next(iter(self.PtDF))

		self.reducedDF = {}
		for key in self.PtDF[ptId].keys():
			if dateStart == 0:
				q2 = [True for i in range(len(self.PtDF[ptId][key]['df'][valueDict[key]]))]#)[0]
			else:
				try:
					q2 = (self.PtDF[ptId][key]['df']['Dates'].astype(object) >= dateStart.replace(tzinfo=utc)).tolist()
				except:
					q2 = (self.PtDF[ptId][key]['df']['Dates'].astype(object) >= dateStart).tolist()
			if dateEnd == 0:
				q3 = [True for i in range(len(self.PtDF[ptId][key]['df'][valueDict[key]]))]#)[0]
			else:
				try:
					q3 = (self.PtDF[ptId][key]['df']['Dates'].astype(object) <= dateEnd.replace(tzinfo=utc)).tolist()
				except:
					q3 = (self.PtDF[ptId][key]['df']['Dates'].astype(object) <= dateEnd).tolist()
			try:
				self.reducedDF[key] = {'display' : self.PtDF[ptId][key]['display'], "df" : self.PtDF[ptId][key]['df'][[a and b for (a, b) in zip(q2, q3)]]}
			except:
				# print(f'No {key} in this time window')
				pass
		self.reducedDF[codes['CGM']]['df'] = self.reducedDF[codes['CGM']]['df'].rename({valueDict[codes['CGM']] : 'CGM', 'root-subject-reference' : 'Patients'}, axis=1)
		self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)'] = self.reducedDF[codes['CGM']]['df']['CGM']/18.0

		for code in codes.keys():
			self.reducedDF[codes[code]]['df'] = self.reducedDF[codes[code]]['df'].rename({valueDict[codes[code]] : code, patientDict[codes[code]] : 'Patients'}, axis=1)

		# self.reducedDF = self.PtDF[ptId]['440404000']['df'][q2 and q3]
		# self.reducedDF = self.reducedDF.rename({'root-valueQuantity-value' : 'CGM', 'root-subject-reference' : 'Patients'}, axis=1)
		# self.reducedDF['CGM (mmol/L)'] = self.reducedDF['CGM']/18.0

	def getStats(self, thrsUL=55, thrsBR=80, thrsAR=200):
		self.statDict ={
			'units' : "mg/dL",
			'mean' : str(round(np.mean(self.reducedDF[codes['CGM']]['df']['CGM']),2)),
			'median' : str(np.median(self.reducedDF[codes['CGM']]['df']['CGM'])),
			'min' : str(np.min(self.reducedDF[codes['CGM']]['df']['CGM'])),
			'max' : str(np.max(self.reducedDF[codes['CGM']]['df']['CGM'])),
			'var' : str(round(np.var(self.reducedDF[codes['CGM']]['df']['CGM']),2)),
			'std' : str(round(np.std(self.reducedDF[codes['CGM']]['df']['CGM']),2)),
			'sum' : str(np.sum(self.reducedDF[codes['CGM']]['df']['CGM'])),
			'q25' : str(np.percentile(self.reducedDF[codes['CGM']]['df']['CGM'], 25)),
			'q50' : str(np.percentile(self.reducedDF[codes['CGM']]['df']['CGM'], 50)),
			'q75' : str(np.percentile(self.reducedDF[codes['CGM']]['df']['CGM'], 75)),
			'utilizationPerc' : str(round(len(self.reducedDF[codes['CGM']]['df']['CGM'])/( ( self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[-1])) - self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[0]))).total_seconds()/60 * 1/5 + 1 ) * 100, 2)),
			'hypoRisk' : self.BGRiskAssesment.LBGRisk(),
			'LowBGIndex' : str(round(self.BGRiskAssesment.LBGI,3)),
			'HighBGIndex' : str(round(self.BGRiskAssesment.HBGI,3)),
			'nDays' : str(int(np.floor( (self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[-1])) - self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[0]))).total_seconds()/3600 * 1/24 + 1 ))),
			'nValues' : str(len(self.reducedDF[codes['CGM']]['df']['CGM'])),
			'nUrgentLow' : str(sum(self.reducedDF[codes['CGM']]['df']['CGM'] < thrsUL)),
			'nBelowRange' : str(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsUL) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsBR))),
			'nInRange' : str(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsBR) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsAR))),
			'nAboveRange' : str(sum(self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsAR)),
			'PerUrgentLow' : str(round(sum(self.reducedDF[codes['CGM']]['df']['CGM'] < thrsUL)/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,2)),
			'PerBelowRange' : str(round(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsUL) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsBR))/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,2)),
			'PerInRange' : str(round(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsBR) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsAR))/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,2)),
			'PerAboveRange' : str(round(sum(self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsAR)/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,2)),
			'CoeffVariation' : str(round(np.std(self.reducedDF[codes['CGM']]['df']['CGM'])/np.mean(self.reducedDF[codes['CGM']]['df']['CGM']),2)),
			'GMI' : str(round(np.mean(self.reducedDF[codes['CGM']]['df']['CGM']) * 0.02392 + 3.31, 2)),
			}
		self.statDict2 ={
			'units' : "mmol/L",
			'mean' : str(round(np.mean(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)']),2)),
			'median' : str(round(np.median(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)']),3)),
			'min' : str(round(np.min(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)']),2)),
			'max' : str(round(np.max(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)']),2)),
			'var' : str(round(np.var(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)']),2)),
			'std' : str(round(np.std(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)']),2)),
			'sum' : str(round(np.sum(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)']),2)),
			'q25' : str(round(np.percentile(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)'], 25),2)),
			'q50' : str(round(np.percentile(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)'], 50),2)),
			'q75' : str(round(np.percentile(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)'], 75),2)),
			'utilizationPerc' : str(round(len(self.reducedDF[codes['CGM']]['df']['CGM'])/( ( self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[-1])) - self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[0]))).total_seconds()/60 * 1/5 + 1 )*100, 2)),
			'hypoRisk' : self.BGRiskAssesment.LBGRisk(),
			'LowBGIndex' : str(round(self.BGRiskAssesment.LBGI,3)),
			'HighBGIndex' : str(round(self.BGRiskAssesment.HBGI,3)),
			'nDays' : str(int(np.floor( (self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[-1])) - self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[0]))).total_seconds()/3600 * 1/24 + 1 ))),
			'nValues' : str(len(self.reducedDF[codes['CGM']]['df']['CGM'])),
			'nUrgentLow' : str(sum(self.reducedDF[codes['CGM']]['df']['CGM'] < thrsUL)),
			'nBelowRange' : str(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsUL) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsBR))),
			'nInRange' : str(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsBR) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsAR))),
			'nAboveRange' : str(sum(self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsAR)),
			'PerUrgentLow' : str(round(sum(self.reducedDF[codes['CGM']]['df']['CGM'] < thrsUL)/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,2)),
			'PerBelowRange' : str(round(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsUL) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsBR))/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,2)),
			'PerInRange' : str(round(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsBR) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsAR))/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,2)),
			'PerAboveRange' : str(round(sum(self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsAR)/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,2)),
			'CoeffVariation' : str(round(np.std(self.reducedDF[codes['CGM']]['df']['CGM'])/np.mean(self.reducedDF[codes['CGM']]['df']['CGM']),2)),
			'GMI' : str(round(np.mean(self.reducedDF[codes['CGM']]['df']['CGM']) * 0.02392 + 3.31, 2)),
			}


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
		for column in statsDF.columns:
			try:
				statsDF[column] = pd.to_numeric(statsDF[column])
			except:
				pass
		return statsDF

	def getStatsDf(self, ndayList = [7,14,21]):
		self.ptAggReducedDF = self.genTmpDf(ndayList)
		self.statDF = self.makeStatsDf(self.ptAggReducedDF)

if __name__ == '__main__':
	dataQuery(date='2021-07-28')


# x=[True,True,False,False]
# y=[True,False,True,False]
# [a and b for a, b in zip(x, y)]
# (np.array(x)*np.array(y)).tolist()
