from utils.observations import ObsDF
from utils.BGriskAssesment import BGRiskAssesment
import pandas as pd
import os
from datetime import datetime
import numpy as np
import json

os.getcwd()
os.chdir(os.path.join(os.getcwd(), "FHIR"))


b = dataObject()
b.BEfolderList
b.typeOfResources
b.dataDict['Observations'][-1]
b.ObsDF
np.unique(b.ObsDF.Patients).tolist()
b.dataDict['Observations'][0]['id']
b.dataDict['Patients']
b.ObsDF[b.ObsDF.apply(lambda x: x['Patients'] == np.unique(b.ObsDF.Patients).tolist()[0], axis=1)]
b.ObsDF[b.ObsDF['Patients'] == np.unique(b.ObsDF.Patients).tolist()[0]]
b.ObsDF[b.ObsDF['Patients'] == ]
df = pd.DataFrame(np.random.randn(5, 3), columns=['a', 'b', 'c'])

df.apply(lambda x: x['b'] > x['c'], axis=1)
df[df.apply(lambda x: x['b'] > x['c'], axis=1)]



class dataObject(object):
	def __init__(self, since='2021-07-21', ptId=0, dateStart=0, dateEnd=0, thrsUL=55, thrsBR=80, thrsAR=200):
		self.getDirectories(since=since)
		self.getResourcesType()
		self.initDict()
		self.loadResource()
		self.dropDuplicates()

		self.getDates()
		self.getCGM()
		self.getPatients()
		self.sortData()
		self.createTable()

		self.saveData()

		# self.getWindow(ptId, dateStart, dateEnd)
		# self.BGRiskAssesment = BGRiskAssesment(self.reducedDF['CGM'])
		# self.getStats(thrsUL, thrsBR, thrsAR)

	def getDirectories(self, since='2021-07-07'):
		self.BEfolderList = []
		for folderName in os.listdir(os.getcwd()):
			if 'TS-BulkExport' in folderName:
				if self.strToDateTime(folderName.split("BulkExport-")[1]) >= self.strToDateTime(since):
					self.BEfolderList.append(folderName)

	def getResourcesType(self):
		self.typeOfResources = []
		typeOfResources = []
		for folder in self.BEfolderList:
			typeOfResources = typeOfResources + os.listdir(os.path.join(os.getcwd(), folder))
		typeOfResources = np.unique(typeOfResources).tolist()
		for typeRes in typeOfResources:
			if typeRes.split(".")[1] == 'json':
				self.typeOfResources.append(typeRes)

	def loadResource(self):
		for folder in self.BEfolderList:
			path = os.path.join(os.getcwd(), folder)
			for file in os.listdir(path):
				if file.split(".")[1] == "json":
					# self.d[file.split(".")[0]].append(self.loadJSON(path, file))
					# self.d[file.split(".")[0]] = self.d[file.split(".")[0]] + self.loadJSON(path, file)
					try:
						self.d[file.split(".")[0]] = self.d[file.split(".")[0]] + self.loadJSON(path, file)
					except:
						self.d[file.split(".")[0]].append(self.loadJSON(path, file))
						print(f'Unable to load {path} {file}')

	def dropDuplicates(self):
		for key in self.d.keys():
			try:
				ids = np.unique([self.d[key][i]['id'] for i in range(len(self.d[key]))]).tolist()
				for id in ids:
					for i in range(len(self.d[key])-1,-1,-1):
						if id == self.d[key][i]['id']:
							self.dataDict[key].append(self.d[key][i])
							break
			except:
				print("Probabbly no ID found for", key)
				self.dataDict[key] = self.d[key]

	def strToDateTime(self,x):
		return datetime.strptime(x, '%Y-%m-%d')

	def initDict(self):
		self.d = {}
		self.dataDict = {}
		for res in self.typeOfResources:
			self.d[res.split(".")[0]] = []
			self.dataDict[res.split(".")[0]] = []

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

	def getDates(self):
		self.dates = [self.getDate(self.dataDict['Observations'][i]['effectiveDateTime']) for i in range(len(self.dataDict['Observations'])) ]

	def getCGM(self):
		self.CGM = [self.dataDict['Observations'][i]['valueQuantity']['value'] for i in range(len(self.dataDict['Observations'])) ]
		self.CGM2 = [self.dataDict['Observations'][i]['valueQuantity']['value']/18 for i in range(len(self.dataDict['Observations'])) ]

	def getPatients(self):
		self.Pts = [self.dataDict['Observations'][i]['subject']['reference'] for i in range(len(self.dataDict['Observations'])) ]

	def sortData(self):
		idx = np.argsort(self.dates)
		self.dates = [self.dates[i] for i in idx]
		self.CGM = [self.CGM[i] for i in idx]
		self.Pts = [self.Pts[i] for i in idx]
		self.CGM2 = [self.CGM2[i] for i in idx]

	def createTable(self):
		self.ObsDF = pd.DataFrame(index=range(len(self.CGM)), columns=['Patients', 'CGM', 'Dates'])
		self.ObsDF['Patients'] = self.Pts
		self.ObsDF['CGM'] = self.CGM
		self.ObsDF['Dates'] = self.dates
		self.ObsDF['CGM (mmol/L)'] = self.CGM2

	def saveData(self):
		dt = str(datetime.now()).split(' ')[0]
		os.path.isdir(os.path.join(os.getcwd(), f'Aggregate-{dt}')) or os.mkdir(os.path.join(os.getcwd(), f'Aggregate-{dt}'))
		#save self.ObsDF
		path = os.path.join(os.getcwd(), f'Aggregate-{dt}')
		self.makeAggDict(path)
		self.ObsDF.to_csv(os.path.join(path, 'Observations.csv'), index=False)
		self.saveJSON(self.aggDict, path, filename='AggDataDict.json')
		#save Dict with b.BEfolderList, self.typeOfResources, patients, IDS, initial date, final date

	def makeAggDict(self, path):
		self.aggDict = {}
		self.aggDict['Directories'] = self.BEfolderList
		self.aggDict['TypeOfResources'] = self.typeOfResources
		self.aggDict['Patients'] = np.unique(self.ObsDF.Patients).tolist()
		self.aggDict['ObsIDs'] = [self.dataDict['Observations'][i]['id'] for i in range(len(self.dataDict['Observations']))]
		self.aggDict['PathToCSV'] = os.path.join(path, 'Observations.csv')


	def getWindow(self, ptId=0, dateStart=0, dateEnd=0):
		if ptId == 0:
			q1 = pd.DataFrame([True for i in range(len(self.CGM))])[0]
		else:
			q1 = self.ObsDF['Patients'] == ptId
		if dateStart == 0:
			q2 = pd.DataFrame([True for i in range(len(self.CGM))])[0]
		else:
			q2 = self.ObsDF['Dates'] >= self.getDate(dateStart)
		if dateEnd == 0:
			q3 = pd.DataFrame([True for i in range(len(self.CGM))])[0]
		else:
			q3 = self.ObsDF['Dates'] <= self.getDate(dateEnd)

		self.reducedDF = self.ObsDF[q1 & q2 & q3]

	def getWindow2(self, ptId=0, dateStart=0, dateEnd=0):
		if ptId == 0:
			q1 = pd.DataFrame([True for i in range(len(self.CGM))])[0]
		else:
			q1 = self.ObsDF['Patients'] == ptId
		if dateStart == 0:
			q2 = pd.DataFrame([True for i in range(len(self.CGM))])[0]
		else:
			q2 = self.ObsDF['Dates'] >= dateStart
		if dateEnd == 0:
			q3 = pd.DataFrame([True for i in range(len(self.CGM))])[0]
		else:
			q3 = self.ObsDF['Dates'] <= dateEnd

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
			'utilizationPerc' : str(round(len(self.reducedDF['CGM'])/( (self.reducedDF['Dates'].iloc[-1] - self.reducedDF['Dates'].iloc[0]).total_seconds()/60 * 1/5 + 1 ),2)),
			'hypoRisk' : self.BGRiskAssesment.LBGRisk(),
			'LowBGIndex' : str(round(self.BGRiskAssesment.LBGI,3)),
			'HighBGIndex' : str(round(self.BGRiskAssesment.HBGI,3)),
			'nDays' : str(int(np.floor( (self.reducedDF['Dates'].iloc[-1] - self.reducedDF['Dates'].iloc[0]).total_seconds()/3600 * 1/24 + 1 ))),
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
			'utilizationPerc' : str(round(len(self.reducedDF['CGM'])/( (self.reducedDF['Dates'].iloc[-1] - self.reducedDF['Dates'].iloc[0]).total_seconds()/60 * 1/5 + 1 ),2)),
			'hypoRisk' : self.BGRiskAssesment.LBGRisk(),
			'LowBGIndex' : str(round(self.BGRiskAssesment.LBGI,3)),
			'HighBGIndex' : str(round(self.BGRiskAssesment.HBGI,3)),
			'nDays' : str(int(np.floor( (self.reducedDF['Dates'].iloc[-1] - self.reducedDF['Dates'].iloc[0]).total_seconds()/3600 * 1/24 + 1 ))),
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
	stats("2021-06-01")
