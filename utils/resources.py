from utils.bulkImport import bulkImport
import pandas as pd
import os

class resources(bulkImport):
	def __init__(self, date = "2021-05-29", MAX=3):
		super(resources, self).__init__(date = date, MAX=MAX)
		'''
			Takes each resource object and turns it into a CSV file.
		'''
		self.initDFDict()
		for key in self.resources.keys():
			try:
				self.createDataFrame(MAX=10, resourceType=key)
				self.createDataFrame(resourceType=key)
				self.createDataFrame(resourceType=key)
			except:
				self.logging.warning(f'resources - Something went wrong when creating the CSV for {key} resource')

	def createDataFrame(self, resourceType = "Observation", MAX=0):
		if MAX > 0 and MAX <= len(self.resources[resourceType]):
			limit = MAX
		else:
			limit = len(self.resources[resourceType])

		idx = self.findLargestRow(resourceType)
		self.temp = self.JSONToDFRow(self.resources[resourceType][idx])
		self.resourcesDF[resourceType] = pd.DataFrame(index=range(limit), columns=self.temp.keys())
		self.logging.info(self.resourcesDF[resourceType].shape)
		for i in range(limit):
			self.temp = self.JSONToDFRow(self.resources[resourceType][i])
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
		string = ''
		for i in l:
			string = string + i + '-'
		return string

	def getStrings(self, array):
		l = dict()
		for i in range(len(array)):
			if array[i][2] != dict:
				l[array[i][0]] = array[i][1]
		return l

	def JSONToDFRow(self, obj, getColumnNames=False):
		tripleArray = list(self.recursive_items(obj))
		rowToDataFrame = self.getStrings(tripleArray)
		return rowToDataFrame

	def findLargestRow(self, resourceType):
		idx = 0
		l = len(self.JSONToDFRow(self.resources[resourceType][idx]))
		for i in range(1, len(self.resources[resourceType])):
			if len(self.JSONToDFRow(self.resources[resourceType][i])) > l:
				idx = i
				l = len(self.JSONToDFRow(self.resources[resourceType][idx]))
		return idx

	def saveDataFrame(self, resourceType='Observations', filename='Observations.csv'):
		self.resourcesDF[resourceType].to_csv(os.path.join(os.getcwd(), self.pathToDump, f'{resourceType}.csv'), index=False)

	def initDFDict(self):
		self.resourcesDF = {}

		for res in self.typeOfResources:
			self.resourcesDF[res] = []


if __name__ == '__main__':
	resources("2021-06-01")
