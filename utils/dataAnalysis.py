import pandas as pd
import os
from datetime import datetime, date, timedelta
import numpy as np
import json
import logging
codeNested = {"Observation" : 'code', "MedicationAdministration" : 'medicationCodeableConcept'}

# os.getcwd()
# os.chdir(os.path.join(os.getcwd(), "FHIR"))


# b = dataObject(since='2021-08-16', concatenate=True)
# b.getCodeIDs()
# b.BEfolderList


# b.AggfolderList
# b.typeOfResources
# len(b.dataDict['Observation'])

# b.dataDict.keys()
# b.dataDict['Questionnaire']
# pd.json_normalize( b.dataDict['Observation'])

class dataObject(object):
	def __init__(self, since='2021-08-06', ptId=0, dateStart=0, dateEnd=0, thrsUL=55, thrsBR=80, thrsAR=200, concatenate=False):
		dt = str(datetime.now()).split(' ')[0]
		self.path = os.path.join(os.getcwd(), f'Complete-{dt}')

		self.getDirectories(since=since, concatenate=concatenate)
		self.getResourcesType()
		self.initDict()
		self.loadResource(concatenate=concatenate)
		self.dropDuplicates()

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
		self.logFunc()

	def getDirectories(self, since='2021-07-07', concatenate=False):
		self.BEfolderList = []
		for folderName in os.listdir(os.getcwd()):
			if 'TS-BulkExport' in folderName:
				if self.strToDateTime(folderName.split("BulkExport-")[1]) >= self.strToDateTime(since):
					self.BEfolderList.append(folderName)
		# self.logging.info(f'Getting data from Dirs {self.BEfolderList}')

		if concatenate:
			try:
				self.AggfolderList = []
				for folderName in os.listdir(os.getcwd()):
					if 'Complete' in folderName:
						# if self.strToDateTime(folderName.split("BulkExport-")[1]) >= self.strToDateTime(since):
						self.AggfolderList.append(folderName)
				idx = 0
				for i, folderName in enumerate(self.AggfolderList):
					if np.abs(self.strToDateTime(since) - self.strToDateTime(folderName.split("Complete-")[1])) < np.abs(self.strToDateTime(since) - self.strToDateTime(self.AggfolderList[idx].split("Complete-")[1])):
						idx = i
				tempList = self.AggfolderList[idx]
				self.AggfolderList = []
				self.AggfolderList.append(tempList)
				# self.logging.info(f'Concatenating it with {self.AggfolderList}')
			except:
				pass
				# self.logging.info(f'No Completed data was found')

	def getResourcesType(self):
		self.typeOfResources = []
		typeOfResources = []
		for folder in self.BEfolderList:
			typeOfResources = typeOfResources + os.listdir(os.path.join(os.getcwd(), folder))
		typeOfResources = np.unique(typeOfResources).tolist()
		for typeRes in typeOfResources:
			if typeRes.split(".")[1] == 'json':
				self.typeOfResources.append(typeRes)

	def loadResource(self, concatenate=False):
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


		if concatenate:
			path = os.path.join(os.getcwd(), self.AggfolderList[0])
			print(path)
			tempData = self.loadJSON(path, 'Data.json')
			for key in self.d.keys():
				try:
					self.d[key] = self.d[key] + tempData[key]
				except:
					pass


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
				# self.logging.info(f'Probabbly no ID found for {key}')
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

	def saveData(self):
		os.path.isdir(self.path) or os.mkdir(self.path)
		#save self.ObsDF
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
		self.aggDict['Codes'] = self.getCodeIDs() #self.parseIDs('Observation')
		self.aggDict['PathToCSV'] = os.path.join(path, 'Observation.csv')

	def getCodeIDs(self):
		self.temp = {}
		for key in ['Observation', 'MedicationAdministration']:
			self.temp[key] = self.parseIDs(key)
		return self.temp

	def parseIDs(self, key):
		print(self.dataDict[key][0][codeNested[key]]['coding'][0]['code'])
		codes = np.unique([self.dataDict[key][i][codeNested[key]]['coding'][0]['code'] for i in range(len(self.dataDict[key]))]).tolist()
		self.dictCodes={}
		for code in codes:
			for i,obs in enumerate(self.dataDict[key]):
				if obs[codeNested[key]]['coding'][0]['code'] == code:
					self.dictCodes[code] = {'display' : obs[codeNested[key]]['coding'][0]['display'], 'system' : obs[codeNested[key]]['coding'][0]['system'], 'resourceType' : key, 'IDs' : []}
					break
		for i,obs in enumerate(self.dataDict[key]):
			code = obs[codeNested[key]]['coding'][0]['code']
			self.dictCodes[code]['IDs'].append(obs['id'])
		return self.dictCodes

	def createDataFrame(self, resourceType = "Observation", MAX=0):
		if MAX > 0 and MAX <= len(self.dataDict[resourceType]):
			limit = MAX
		else:
			limit = len(self.dataDict[resourceType])
		# for code in self.Codes:
		# 	for obs in self.dataDict['Observations']

		idx = self.findLargestRow(resourceType)
		temp = self.JSONToDFRow(self.dataDict[resourceType][idx])
		self.resourcesDF[resourceType] = pd.DataFrame(index=range(limit), columns=temp.keys())
		# self.logging.info(self.resourcesDF[resourceType].shape)
		for i in range(limit):
			temp = self.JSONToDFRow(self.dataDict[resourceType][i])
			for key in temp:
				self.resourcesDF[resourceType].iloc[i][key] = temp[key]

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
			if type(value) is list:
				self.isList(dictionary, key)
			elif type(value) is dict:
				yield (key, value, type(value))
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

	def findLargestRow(self, resourceType):
		idx = 0
		l = len(self.JSONToDFRow(self.dataDict[resourceType][idx]))
		for i in range(1, len(self.dataDict[resourceType])):
			if len(self.JSONToDFRow(self.dataDict[resourceType][i])) > l:
				idx = i
				l = len(self.JSONToDFRow(self.dataDict[resourceType][idx]))
		return idx

	def initDFDict(self):
		self.resourcesDF = {}

		for res in self.typeOfResources:
			self.resourcesDF[res.split(".")[0]] = []

	def saveDataFrame(self, resourceType='Observations', filename='Observations.csv'):
		self.resourcesDF[resourceType].to_csv(os.path.join(self.path, f'{resourceType}.csv'), index=False)

	def logFunc(self):
		self.initTime = datetime.now()
		self.logging = logging
		os.path.isdir(os.path.join(os.getcwd(), self.path)) or os.mkdir(os.path.join(os.getcwd(), self.path))
		self.logging.basicConfig(filename=os.path.join(os.getcwd(), self.path, 'Complete.log'), level=logging.DEBUG)
		self.logging.info('#######################################################################################')
		self.logging.info(f'{str(self.initTime).split(".")[0]} - Concatenating data')
		self.logging.info(f'inOut - Data dumped in {self.path}')
		self.logging.info(f'Getting data from Dirs {self.BEfolderList}')
		try:
			self.logging.info(f'Concatenating it with {self.AggfolderList}')
		except:
			self.logging.info(f'No Completed data was found')


if __name__ == '__main__':
	dataObject(since='2021-08-03', concatenate=False)
