from utils.BGriskAssesment import BGRiskAssesment
import pandas as pd
import os
from datetime import datetime
import numpy as np
import json

# os.getcwd()
# os.chdir(os.path.join(os.getcwd(), "FHIR"))

# b = dataQuery()
# b.aggDict['PathToCSV']
# ag = b.loadJSON(os.path.join(os.getcwd(), 'Aggregate-2021-07-28'), 'AggDataDict.json')
# ag.keys()
# b.aggDict['Patients']
# len(b.ObsDF['CGM'])
# b.PtDF.keys()
# b.PtDF['Patient/325498']['CGM']
# b.ObsDF
# b.reducedDF
# b.getDate(str(b.ObsDF['Dates']))
# b.ObsDF['Dates'].apply(lambda x : b.getDate(str(x)))
# b.reducedDF
# b.getDate(str(b.reducedDF['Dates'].iloc[0]))
# b.ObsDF
# b.ObsDF.apply(lambda x : b.getDate(str(x['Dates'])), axis=1)

class dataQuery(object):
	def __init__(self, date='2021-07-28', ptId=0, dateStart=0, dateEnd=0, thrsUL=55, thrsBR=80, thrsAR=200):
		self.aggDict = self.loadJSON(os.path.join(os.getcwd(), 'Aggregate-' + date), 'AggDataDict.json')
		# self.ObsDF = pd.read_csv(self.aggDict['PathToCSV'])
		self.ObsDF = pd.read_csv(os.path.join(os.getcwd(), 'Aggregate-' + date, 'Observation.csv'))
		self.ObsDF['Dates'] = self.ObsDF.apply(lambda x : self.getDate(str(x['Dates'])), axis=1)
		self.createPtDF()

		self.BGRiskAssesment = BGRiskAssesment(self.reducedDF['CGM'])

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
				return datetime.fromisoformat(x[:-1])
			except:
				return datetime.fromisoformat(x[:])

	def createPtDF(self):
		self.PtDF = {}
		for pt in self.aggDict['Patients']:
			self.PtDF[pt] = self.getWindow(ptId=pt)


	def getWindow(self, ptId=0, dateStart=0, dateEnd=0):
		if ptId == 0:
			q1 = pd.DataFrame([True for i in range(len(self.ObsDF['CGM']))])[0]
		else:
			q1 = self.ObsDF['Patients'] == ptId
		if dateStart == 0:
			q2 = pd.DataFrame([True for i in range(len(self.ObsDF['CGM']))])[0]
		else:
			q2 = self.ObsDF['Dates'] >= self.getDate(dateStart)
		if dateEnd == 0:
			q3 = pd.DataFrame([True for i in range(len(self.ObsDF['CGM']))])[0]
		else:
			q3 = self.ObsDF['Dates'] <= self.getDate(dateEnd)

		self.reducedDF = self.ObsDF[q1 & q2 & q3]
		return self.ObsDF[q1 & q2 & q3]

	def getWindow2(self, ptId=0, dateStart=0, dateEnd=0):
		if ptId == 0:
			q1 = pd.DataFrame([True for i in range(len(self.ObsDF['CGM']))])[0]
		else:
			q1 = self.ObsDF['Patients'] == ptId
		if dateStart == 0:
			q2 = pd.DataFrame([True for i in range(len(self.ObsDF['CGM']))])[0]
		else:
			q2 = self.ObsDF['Dates'] >= dateStart
		if dateEnd == 0:
			q3 = pd.DataFrame([True for i in range(len(self.ObsDF['CGM']))])[0]
		else:
			q3 = self.ObsDF['Dates'] <= dateEnd

		self.reducedDF = self.ObsDF[q1 & q2 & q3]

	def getWindow3(self, ptId=0, dateStart=0, dateEnd=0):
		if ptId == 'All':
			q1 = pd.DataFrame([True for i in range(len(self.ObsDF['CGM']))])[0]
		else:
			q1 = self.ObsDF['Patients'] == ptId
		if dateStart == 0:
			q2 = pd.DataFrame([True for i in range(len(self.ObsDF['CGM']))])[0]
		else:
			q2 = self.ObsDF['Dates'].apply(lambda x : self.getDate(str(x))) >= dateStart
		if dateEnd == 0:
			q3 = pd.DataFrame([True for i in range(len(self.ObsDF['CGM']))])[0]
		else:
			q3 = self.ObsDF['Dates'].apply(lambda x : self.getDate(str(x))) <= dateEnd

		self.reducedDF = self.ObsDF[q1 & q2 & q3]

	def getStats(self, thrsUL=55, thrsBR=80, thrsAR=200):
		self.statDict ={
			'units' : "mg/dL",
			'mean' : str(round(np.mean(self.reducedDF['CGM']),3)),
			'median' : str(np.median(self.reducedDF['CGM'])),
			'min' : str(np.min(self.reducedDF['CGM'])),
			'max' : str(np.max(self.reducedDF['CGM'])),
			'var' : str(round(np.var(self.reducedDF['CGM']),3)),
			'std' : str(round(np.std(self.reducedDF['CGM']),3)),
			'sum' : str(np.sum(self.reducedDF['CGM'])),
			'q25' : str(np.percentile(self.reducedDF['CGM'], 25)),
			'q50' : str(np.percentile(self.reducedDF['CGM'], 50)),
			'q75' : str(np.percentile(self.reducedDF['CGM'], 75)),
			'utilizationPerc' : str(round(len(self.reducedDF['CGM'])/( ( self.getDate(str(self.reducedDF['Dates'].iloc[-1])) - self.getDate(str(self.reducedDF['Dates'].iloc[0]))).total_seconds()/60 * 1/5 + 1 ),2)),
			'hypoRisk' : self.BGRiskAssesment.LBGRisk(),
			'LowBGIndex' : str(round(self.BGRiskAssesment.LBGI,3)),
			'HighBGIndex' : str(round(self.BGRiskAssesment.HBGI,3)),
			'nDays' : str(int(np.floor( (self.getDate(str(self.reducedDF['Dates'].iloc[-1])) - self.getDate(str(self.reducedDF['Dates'].iloc[0]))).total_seconds()/3600 * 1/24 + 1 ))),
			'nValues' : str(len(self.reducedDF['CGM'])),
			'nUrgentLow' : str(sum(self.reducedDF['CGM'] < thrsUL)),
			'nBelowRange' : str(sum((self.reducedDF['CGM'] >= thrsUL) & (self.reducedDF['CGM'] < thrsBR))),
			'nInRange' : str(sum((self.reducedDF['CGM'] >= thrsBR) & (self.reducedDF['CGM'] < thrsAR))),
			'nAboveRange' : str(sum(self.reducedDF['CGM'] >= thrsAR)),
			'PerUrgentLow' : str(round(sum(self.reducedDF['CGM'] < thrsUL)/len(self.reducedDF['CGM']),3)),
			'PerBelowRange' : str(round(sum((self.reducedDF['CGM'] >= thrsUL) & (self.reducedDF['CGM'] < thrsBR))/len(self.reducedDF['CGM']),3)),
			'PerInRange' : str(round(sum((self.reducedDF['CGM'] >= thrsBR) & (self.reducedDF['CGM'] < thrsAR))/len(self.reducedDF['CGM']),3)),
			'PerAboveRange' : str(round(sum(self.reducedDF['CGM'] >= thrsAR)/len(self.reducedDF['CGM']),3)),
			'CoeffVariation' : str(round(np.std(self.reducedDF['CGM'])/np.mean(self.reducedDF['CGM']),3)),
			'GMI' : str(round(np.mean(self.reducedDF['CGM']) * 0.02392 + 3.31, 3)),
			}
		self.statDict2 ={
			'units' : "mmol/L",
			'mean' : str(round(np.mean(self.reducedDF['CGM (mmol/L)']),3)),
			'median' : str(round(np.median(self.reducedDF['CGM (mmol/L)']),3)),
			'min' : str(round(np.min(self.reducedDF['CGM (mmol/L)']),3)),
			'max' : str(round(np.max(self.reducedDF['CGM (mmol/L)']),3)),
			'var' : str(round(np.var(self.reducedDF['CGM (mmol/L)']),3)),
			'std' : str(round(np.std(self.reducedDF['CGM (mmol/L)']),3)),
			'sum' : str(round(np.sum(self.reducedDF['CGM (mmol/L)']),3)),
			'q25' : str(round(np.percentile(self.reducedDF['CGM (mmol/L)'], 25),3)),
			'q50' : str(round(np.percentile(self.reducedDF['CGM (mmol/L)'], 50),3)),
			'q75' : str(round(np.percentile(self.reducedDF['CGM (mmol/L)'], 75),3)),
			'utilizationPerc' : str(round(len(self.reducedDF['CGM'])/( ( self.getDate(str(self.reducedDF['Dates'].iloc[-1])) - self.getDate(str(self.reducedDF['Dates'].iloc[0]))).total_seconds()/60 * 1/5 + 1 ),2)),
			'hypoRisk' : self.BGRiskAssesment.LBGRisk(),
			'LowBGIndex' : str(round(self.BGRiskAssesment.LBGI,3)),
			'HighBGIndex' : str(round(self.BGRiskAssesment.HBGI,3)),
			'nDays' : str(int(np.floor( (self.getDate(str(self.reducedDF['Dates'].iloc[-1])) - self.getDate(str(self.reducedDF['Dates'].iloc[0]))).total_seconds()/3600 * 1/24 + 1 ))),
			'nValues' : str(len(self.reducedDF['CGM'])),
			'nUrgentLow' : str(sum(self.reducedDF['CGM'] < thrsUL)),
			'nBelowRange' : str(sum((self.reducedDF['CGM'] >= thrsUL) & (self.reducedDF['CGM'] < thrsBR))),
			'nInRange' : str(sum((self.reducedDF['CGM'] >= thrsBR) & (self.reducedDF['CGM'] < thrsAR))),
			'nAboveRange' : str(sum(self.reducedDF['CGM'] >= thrsAR)),
			'PerUrgentLow' : str(round(sum(self.reducedDF['CGM'] < thrsUL)/len(self.reducedDF['CGM']),3)),
			'PerBelowRange' : str(round(sum((self.reducedDF['CGM'] >= thrsUL) & (self.reducedDF['CGM'] < thrsBR))/len(self.reducedDF['CGM']),3)),
			'PerInRange' : str(round(sum((self.reducedDF['CGM'] >= thrsBR) & (self.reducedDF['CGM'] < thrsAR))/len(self.reducedDF['CGM']),3)),
			'PerAboveRange' : str(round(sum(self.reducedDF['CGM'] >= thrsAR)/len(self.reducedDF['CGM']),3)),
			'CoeffVariation' : str(round(np.std(self.reducedDF['CGM'])/np.mean(self.reducedDF['CGM']),3)),
			'GMI' : str(round(np.mean(self.reducedDF['CGM']) * 0.02392 + 3.31, 3)),
			}

if __name__ == '__main__':
	dataQuery(date='2021-07-28')
