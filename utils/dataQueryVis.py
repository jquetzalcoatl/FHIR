from utils.BGriskAssesment import BGRiskAssesment
from utils.dataTuples import codeDict, dateDict, codes, valueDict
import pandas as pd
import os
from datetime import datetime
import numpy as np
import json
import pytz
utc=pytz.UTC

# os.getcwd()
# os.chdir(os.path.join(os.getcwd(), "FHIR"))

# # codeDict = {'Observation' : 'root-code-coding-coding_0-code', 'MedicationAdministration' : 'root-medicationCodeableConcept-coding-coding_0-code'}
# # dateDict = {'Observation' : 'root-effectiveDateTime', 'MedicationAdministration' : 'root-effectiveDateTime', 'Consent' : 'root-dateTime'}
#

# b = dataQuery(date='2021-09-22')
# np.unique(b.dfResDict['MedicationAdministration']['root-medicationCodeableConcept-coding-coding_0-code'])#['root-subject-reference'])#.keys()#['Observation']
# b.dfCodeDict
# b.PtDF.keys()
# b.PtDF.keys()#['9059-7']['df']['root-valueQuantity-code']
# 'root-valueQuantity-value' '9059-7'
# b.PtDF['Patient/460111']['39543009']['df']#.keys()
# b.PtDF['Patient/460111']['9059-7']['df']#.columns#['root-valueQuantity-value']
# # b.PtDF['Patient/2023']["9059-7"]['df']
# b.dfCodeDict['39543009']['df']['root-dosage-dose-code']
# b.reducedDF['39543009']['df']





class dataQuery(object):
	def __init__(self, date='2021-09-10', ptId=0, dateStart=0, dateEnd=0, thrsUL=55, thrsBR=80, thrsAR=200):
		self.metadata = self.loadJSON(os.path.join(os.getcwd(), 'Complete-' + date), 'Metadata.json')
		# self.metadata = self.loadJSON(os.path.join(os.getcwd(), 'Complete-' + date), 'AggDataDict.json')
		self.dataDict = self.loadJSON(os.path.join(os.getcwd(), 'Complete-' + date), 'Data.json')
		# self.ObsDF = pd.read_csv(os.path.join(os.getcwd(), 'Complete-' + date, 'Observation.csv'))

		fileList = os.listdir(os.path.join(os.getcwd(), f'Complete-{date}'))
		fLBool = [file.split(".")[1] == "csv" for file in fileList ]
		resList = [ file.split(".")[0] for i,file in enumerate(fileList) if fLBool[i] == True ]
		self.dfResDict = {}
		for key in resList:
			self.dfResDict[key] = pd.read_csv(os.path.join(os.getcwd(), 'Complete-' + date, f'{key}.csv'))
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

		self.reducedDF[codes['CGM']]['df'] = self.reducedDF[codes['CGM']]['df'].rename({valueDict[codes['CGM']] : 'CGM', 'root-subject-reference' : 'Patients'}, axis=1)
		self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)'] = self.reducedDF[codes['CGM']]['df']['CGM']/18.0

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

		# self.reducedDF = self.PtDF[ptId]['440404000']['df'][q2 and q3]
		# self.reducedDF = self.reducedDF.rename({'root-valueQuantity-value' : 'CGM', 'root-subject-reference' : 'Patients'}, axis=1)
		# self.reducedDF['CGM (mmol/L)'] = self.reducedDF['CGM']/18.0

	def getStats(self, thrsUL=55, thrsBR=80, thrsAR=200):
		self.statDict ={
			'units' : "mg/dL",
			'mean' : str(round(np.mean(self.reducedDF[codes['CGM']]['df']['CGM']),3)),
			'median' : str(np.median(self.reducedDF[codes['CGM']]['df']['CGM'])),
			'min' : str(np.min(self.reducedDF[codes['CGM']]['df']['CGM'])),
			'max' : str(np.max(self.reducedDF[codes['CGM']]['df']['CGM'])),
			'var' : str(round(np.var(self.reducedDF[codes['CGM']]['df']['CGM']),3)),
			'std' : str(round(np.std(self.reducedDF[codes['CGM']]['df']['CGM']),3)),
			'sum' : str(np.sum(self.reducedDF[codes['CGM']]['df']['CGM'])),
			'q25' : str(np.percentile(self.reducedDF[codes['CGM']]['df']['CGM'], 25)),
			'q50' : str(np.percentile(self.reducedDF[codes['CGM']]['df']['CGM'], 50)),
			'q75' : str(np.percentile(self.reducedDF[codes['CGM']]['df']['CGM'], 75)),
			'utilizationPerc' : str(round(len(self.reducedDF[codes['CGM']]['df']['CGM'])/( ( self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[-1])) - self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[0]))).total_seconds()/60 * 1/5 + 1 ),2)),
			'hypoRisk' : self.BGRiskAssesment.LBGRisk(),
			'LowBGIndex' : str(round(self.BGRiskAssesment.LBGI,3)),
			'HighBGIndex' : str(round(self.BGRiskAssesment.HBGI,3)),
			'nDays' : str(int(np.floor( (self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[-1])) - self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[0]))).total_seconds()/3600 * 1/24 + 1 ))),
			'nValues' : str(len(self.reducedDF[codes['CGM']]['df']['CGM'])),
			'nUrgentLow' : str(sum(self.reducedDF[codes['CGM']]['df']['CGM'] < thrsUL)),
			'nBelowRange' : str(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsUL) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsBR))),
			'nInRange' : str(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsBR) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsAR))),
			'nAboveRange' : str(sum(self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsAR)),
			'PerUrgentLow' : str(round(sum(self.reducedDF[codes['CGM']]['df']['CGM'] < thrsUL)/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,3)),
			'PerBelowRange' : str(round(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsUL) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsBR))/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,3)),
			'PerInRange' : str(round(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsBR) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsAR))/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,3)),
			'PerAboveRange' : str(round(sum(self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsAR)/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,3)),
			'CoeffVariation' : str(round(np.std(self.reducedDF[codes['CGM']]['df']['CGM'])/np.mean(self.reducedDF[codes['CGM']]['df']['CGM']),3)),
			'GMI' : str(round(np.mean(self.reducedDF[codes['CGM']]['df']['CGM']) * 0.02392 + 3.31, 3)),
			}
		self.statDict2 ={
			'units' : "mmol/L",
			'mean' : str(round(np.mean(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)']),3)),
			'median' : str(round(np.median(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)']),3)),
			'min' : str(round(np.min(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)']),3)),
			'max' : str(round(np.max(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)']),3)),
			'var' : str(round(np.var(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)']),3)),
			'std' : str(round(np.std(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)']),3)),
			'sum' : str(round(np.sum(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)']),3)),
			'q25' : str(round(np.percentile(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)'], 25),3)),
			'q50' : str(round(np.percentile(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)'], 50),3)),
			'q75' : str(round(np.percentile(self.reducedDF[codes['CGM']]['df']['CGM (mmol/L)'], 75),3)),
			'utilizationPerc' : str(round(len(self.reducedDF[codes['CGM']]['df']['CGM'])/( ( self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[-1])) - self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[0]))).total_seconds()/60 * 1/5 + 1 )*100,2)),
			'hypoRisk' : self.BGRiskAssesment.LBGRisk(),
			'LowBGIndex' : str(round(self.BGRiskAssesment.LBGI,3)),
			'HighBGIndex' : str(round(self.BGRiskAssesment.HBGI,3)),
			'nDays' : str(int(np.floor( (self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[-1])) - self.getDate(str(self.reducedDF[codes['CGM']]['df']['Dates'].iloc[0]))).total_seconds()/3600 * 1/24 + 1 ))),
			'nValues' : str(len(self.reducedDF[codes['CGM']]['df']['CGM'])),
			'nUrgentLow' : str(sum(self.reducedDF[codes['CGM']]['df']['CGM'] < thrsUL)),
			'nBelowRange' : str(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsUL) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsBR))),
			'nInRange' : str(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsBR) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsAR))),
			'nAboveRange' : str(sum(self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsAR)),
			'PerUrgentLow' : str(round(sum(self.reducedDF[codes['CGM']]['df']['CGM'] < thrsUL)/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,3)),
			'PerBelowRange' : str(round(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsUL) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsBR))/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,3)),
			'PerInRange' : str(round(sum((self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsBR) & (self.reducedDF[codes['CGM']]['df']['CGM'] < thrsAR))/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,3)),
			'PerAboveRange' : str(round(sum(self.reducedDF[codes['CGM']]['df']['CGM'] >= thrsAR)/len(self.reducedDF[codes['CGM']]['df']['CGM'])*100,3)),
			'CoeffVariation' : str(round(np.std(self.reducedDF[codes['CGM']]['df']['CGM'])/np.mean(self.reducedDF[codes['CGM']]['df']['CGM']),3)),
			'GMI' : str(round(np.mean(self.reducedDF[codes['CGM']]['df']['CGM']) * 0.02392 + 3.31, 3)),
			}

if __name__ == '__main__':
	dataQuery(date='2021-07-28')


# x=[True,True,False,False]
# y=[True,False,True,False]
# [a and b for a, b in zip(x, y)]
# (np.array(x)*np.array(y)).tolist()
