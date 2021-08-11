# from utils.observations import ObsDF
# from utils.BGriskAssesment import BGRiskAssesment
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
b.dataDict['Observation'][-1]

b.resourcesDF.keys()


b.dataDict['Observation'][oID[2]]
b.dataDict['Observation'][oID2[0]]


class dataObject(object):
	def __init__(self, since='2021-07-29', ptId=0, dateStart=0, dateEnd=0, thrsUL=55, thrsBR=80, thrsAR=200):
		self.getDirectories(since=since)
		self.getResourcesType()
		self.initDict()
		self.loadResource()
		self.dropDuplicates()

		# self.getDates()
		# self.getCGM()
		# self.getPatients()
		# self.sortData()
		# self.createTable()

		self.saveData()

		self.initDFDict()
		for key in self.dataDict.keys():
			try:
				self.createDataFrame(MAX=10, resourceType=key)
				self.createDataFrame(resourceType=key)
				self.createDataFrame(resourceType=key)
			except:
				pass
				# self.logging.info(f'Something went wrong when creating the CSV for {key} resource')

		####################################################

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
		self.dates = [self.getDate(self.dataDict['Observation'][i]['effectiveDateTime']) for i in range(len(self.dataDict['Observation'])) ]

	def getCGM(self):
		self.CGM = [self.dataDict['Observation'][i]['valueQuantity']['value'] for i in range(len(self.dataDict['Observation'])) ]
		self.CGM2 = [self.dataDict['Observation'][i]['valueQuantity']['value']/18 for i in range(len(self.dataDict['Observation'])) ]

	def getPatients(self):
		self.Pts = [self.dataDict['Observation'][i]['subject']['reference'] for i in range(len(self.dataDict['Observation'])) ]

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
		self.path = os.path.join(os.getcwd(), f'Aggregate-{dt}')
		self.makeAggDict(self.path)
		# self.ObsDF.to_csv(os.path.join(path, 'Observation.csv'), index=False)
		self.saveJSON(self.aggDict, self.path, filename='Metadata.json')
		self.saveJSON(self.dataDict, self.path, filename='Data.json')
		#save Dict with b.BEfolderList, self.typeOfResources, patients, IDS, initial date, final date

	def makeAggDict(self, path):
		self.aggDict = {}
		self.aggDict['Directories'] = self.BEfolderList
		self.aggDict['TypeOfResources'] = self.typeOfResources
		self.aggDict['Patients'] = np.unique([self.dataDict['Observation'][i]['subject']['reference'] for i in range(len(self.dataDict['Observation']))]).tolist()#np.unique(self.ObsDF.Patients).tolist()
		self.aggDict['ObsIDs'] = [self.dataDict['Observation'][i]['id'] for i in range(len(self.dataDict['Observation']))]
		self.aggDict['Codes'] = self.parseIDs()
		self.aggDict['PathToCSV'] = os.path.join(path, 'Observation.csv')

	def parseIDs(self):
		codes = np.unique([self.dataDict['Observation'][i]['code']['coding'][0]['code'] for i in range(len(self.dataDict['Observation']))]).tolist()
		self.dictCodes={}
		for code in codes:
			for i,obs in enumerate(self.dataDict['Observation']):
				if obs['code']['coding'][0]['code'] == code:
					self.dictCodes[code] = {'display' : obs['code']['coding'][0]['display'], 'system' : obs['code']['coding'][0]['system'], 'IDs' : []}
					break
		for i,obs in enumerate(self.dataDict['Observation']):
			code = obs['code']['coding'][0]['code']
			self.dictCodes[code]['IDs'].append(obs['id'])
		return self.dictCodes

	def createDataFrame(self, resourceType = "Observation", MAX=0):
		if MAX > 0 and MAX <= len(self.dataDict[resourceType]):
			limit = MAX
		else:
			limit = len(self.dataDict[resourceType])
		# for code in self.Codes:
		# 	for obs in self.dataDict['Observations']

		self.temp = self.JSONToDFRow(self.dataDict[resourceType][0])
		self.resourcesDF[resourceType] = pd.DataFrame(index=range(limit), columns=self.temp.keys())
		# self.logging.info(self.resourcesDF[resourceType].shape)
		for i in range(limit):
			self.temp = self.JSONToDFRow(self.dataDict[resourceType][i])
			for key in self.temp:
				self.resourcesDF[resourceType].iloc[i][key] = self.temp[key]

		self.saveDataFrame(resourceType = resourceType)

	def isList(self, d, keyword):
		if type(d.get(keyword)) == list:
			keywordUP = keyword.upper()
			d[keywordUP] = d[keyword]
			d[keyword] = {}
			for i, el in enumerate(d[keywordUP]):
				d[keyword][f'{keyword}_{i}'] = d[keywordUP][i]
			d.pop(keywordUP, None)

	def recursive_items(self, dictionary, prepend = ['root']):
		'''
		https://stackoverflow.com/questions/39233973/get-all-keys-of-a-nested-dictionary
		'''
		for key, value in dictionary.items():
			# print(type(value))
			if type(value) is list:
				# print(key)
				self.isList(dictionary, key)
			elif type(value) is dict:
				yield (key, value, type(value))
				# prepend.append(key)
				yield from self.recursive_items(value, prepend + [key])
			else:
				string = self.listToString(prepend)
				yield (f'{string}{key}', value, type(value))

	def listToString(self, l):
		# string =
		string = ''
		for i in l:
			string = string + i + '-'
		return string

	def getStrings(self, array):
		l = dict()
		for i in range(len(array)):
			if array[i][2] != dict:
				# l.append({arr[i][0] : arr[i][1]})
				l[array[i][0]] = array[i][1]
		return l

	def JSONToDFRow(self, obj, getColumnNames=False):
		tripleArray = list(self.recursive_items(obj))
		rowToDataFrame = self.getStrings(tripleArray)
		# if getColumnNames:
		#     return rowToDataFrame.keys()
		# else:
		#     return list(rowToDataFrame.values())
		return rowToDataFrame

	def initDFDict(self):
		self.resourcesDF = {}

		for res in self.typeOfResources:
			self.resourcesDF[res.split(".")[0]] = []

	def saveDataFrame(self, resourceType='Observations', filename='Observations.csv'):
		self.resourcesDF[resourceType].to_csv(os.path.join(self.path, f'{resourceType}.csv'), index=False)


if __name__ == '__main__':
	stats("2021-06-01")
