string = 'Hydrogen'

import matplotlib.pyplot as plt
import matplotlib as mpl

###
import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime
import time
import os
import logging

# PATH = "https://trustsphere.demo.smilecdr.com/fhir-request/Observation?code=440404000&subject=Patient/292046&date=lt2021-05-30T00:00:00Z&date=gt2021-05-15T00:00:00Z"
# PATH = "https://trustsphere.demo.smilecdr.com/fhir-request/$export?_since=2021-05-29T00:00:00Z"
# requests.get('https://api.github.com/user', auth=('user', 'pass'))

class inOut(object):
	def __init__(self, date = "2021-05-29", group_id="CONSENT-GIVEN-GROUP", MAX=3):
		'''
			Consider this to be a box that takes in an initial date and will
			pull and parse all the data since then concerning Observations,
			MedicationAdministration, Patients, etc.

			While the data we're after are the previously mentioned. There are
			several by-products. All by-products are also parsed as JSON and
			saved in a directory named "TS-BulkExport-DATE".

			This object initializes a path variable that is going to be feed
			to requests.get for the bulk export. The date since for the bulk
			export can be given as an input. There are as many lists
			as resources, i.e., Obs => Observations,
			Meds => MedicationAdministration, Patients => Patient.
		'''

		self.dt = str(datetime.now()).split(' ')[0]
		self.path = "https://trustsphere.demo.smilecdr.com/fhir-request/$export?_since=" + date + "T00:00:00Z"
		# self.path = "http://trustsphere.demo.smilecdr.com/fhir-request/Group/" + group_id + "/$export?_since=" + date + "T00:00:00Z"
		self.pathToDump = 'TS-BulkExport-' + self.dt
		self.Obs = []
		self.Group = []
		self.Meds = []
		self.Patients = []
		self.CodeSystem = []
		self.Questionnaire = []
		self.QuestionnaireResponse = []

		# PUT -> server consent w/o and participants
		self.logFunc()
		self.getBinaryLinks()
		self.initDict()
		self.getAllBinaries(MAX=MAX)
		self.logging.info('inOut - Binaries Loaded!')

	def getBinaryLinks(self):
		self.BulkRequest = requests.get(self.path, headers={"Prefer" : "respond-async"})
		self.BulkRequestHeaderDict = dict(self.BulkRequest.headers)
		self.binariesRequest = requests.get(self.BulkRequestHeaderDict['Content-Location'])

		try:
			while dict(self.binariesRequest.headers)['Retry-After'] == '120':
				self.logging.info('inOut - Binaries not ready yet...sleep 120s')
				time.sleep(120)
				self.binariesRequest = requests.get(self.BulkRequestHeaderDict['Content-Location'])
		except:
			self.logging.info("inOut - Binary Links are ready")

		self.binariesRequestDict = json.loads(self.binariesRequest.text.replace("\n", "").replace(" ",""))

		self.saveJSON(self.BulkRequestHeaderDict, f'BulkRequestHeaderDict.json')
		self.logging.info("inOut - BulkRequestHeaderDict object saved")
		self.saveJSON(self.binariesRequestDict, f'binariesRequestDict.json')
		self.logging.info("inOut - binariesRequestDict object saved")

	def getAllBinaries(self, MAX=0):
		l = len(self.binariesRequestDict['output'])
		if MAX > 0 and MAX <= len(self.binariesRequestDict['output']):
			limit = MAX
		else:
			limit = len(self.binariesRequestDict['output'])
		self.logging.info(f'Getting {limit} out of {l} binaries.')
		for i in range(limit):
			try:
				temp = requests.get(self.binariesRequestDict['output'][i]['url'])
				sep = list(np.unique(list(self.find_all(temp.text, '\n'))))
				typeRes = self.binariesRequestDict['output'][i]['type']
				self.resources[typeRes] = self.resources[typeRes] + self.parseJSON(temp.text,sep)

				# if self.binariesRequestDict['output'][i]['type'] == 'Observation':
				#     self.Obs = self.Obs +  self.parseJSON(temp.text,sep)
				# elif self.binariesRequestDict['output'][i]['type'] == 'MedicationAdministration':
				#     self.Meds = self.Meds +  self.parseJSON(temp.text,sep)
				# elif self.binariesRequestDict['output'][i]['type'] == 'Patient':
				#     self.Patients = self.Patients + self.parseJSON(temp.text,sep)
				# elif self.binariesRequestDict['output'][i]['type'] == 'CodeSystem':
				#     self.CodeSystem = self.CodeSystem + self.parseJSON(temp.text,sep)
				# elif self.binariesRequestDict['output'][i]['type'] == 'Questionnaire':
				#     self.Questionnaire = self.Questionnaire + self.parseJSON(temp.text,sep)
				# elif self.binariesRequestDict['output'][i]['type'] == 'QuestionnaireResponse':
				#     self.QuestionnaireResponse = self.QuestionnaireResponse + self.parseJSON(temp.text,sep)
				# elif self.binariesRequestDict['output'][i]['type'] == 'Group':
				#     self.Group = self.Group + self.parseJSON(temp.text,sep)
			except:
				self.logging.warning(f'inOut - Binary with index {i} was not loaded.')

		# self.typeOfResources = list(np.unique([self.binariesRequestDict['output'][i]['type'] for i in range(len(self.binariesRequestDict['output']))]))
		self.logging.info(f'type of resources: {self.typeOfResources}')
		self.logging.info(f'inOut - \n')
		for key in self.resources.keys():
			m = len(self.resources[key])
			self.logging.info(f'Number of {key} resources = {m} \n')
			if m > 0:
				self.saveJSON(self.resources[key], f'{key}.json')
				self.logging.info(f'inOut - {key} resource object saved')

		# self.logging.info(f'inOut - \n Number of observations: {len(self.Obs)} \n Number of MedicationAdministration: {len(self.Meds)} \n Number of Patients: {len(self.Patients)} \n Number of CodeSystem: {len(self.CodeSystem)} \n Number of Questionnaire: {len(self.Questionnaire)} \n Number of QuestionnaireResponse: {len(self.QuestionnaireResponse)} \n Number of Groups: {len(self.Group)} \n')

		# if len(self.Obs) > 0:
		#     self.saveJSON(self.Obs, f'Observations.json')
		#     self.logging.info("inOut - Observations object saved")
		# if len(self.Meds) > 0:
		#     self.saveJSON(self.Meds, f'MedicationAdministration.json')
		#     self.logging.info("inOut - MedicationAdministration object saved")
		# if len(self.Patients) > 0:
		#     self.saveJSON(self.Patients, f'Patients.json')
		#     self.logging.info("inOut - Patients object saved")
		# if len(self.CodeSystem) > 0:
		#     self.saveJSON(self.CodeSystem, f'CodeSystem.json')
		#     self.logging.info("inOut - CodeSystem object saved")
		# if len(self.Questionnaire) > 0:
		#     self.saveJSON(self.Questionnaire, f'Questionnaire.json')
		#     self.logging.info("inOut - Questionnaire object saved")
		# if len(self.QuestionnaireResponse) > 0:
		#     self.saveJSON(self.QuestionnaireResponse, f'QuestionnaireResponse.json')
		#     self.logging.info("inOut - QuestionnaireResponse object saved")
		# if len(self.Group) > 0:
		#     self.saveJSON(self.Group, f'Group.json')
		#     self.logging.info("inOut - Group object saved")

	def find_all(self, a_str, sub):
		'''
			Receives a String and a pattern. Returns the positions where
			the pattern sub is located. This is used to parse the binaries, by
			first separating into blocks separated by newlines (\n)
		'''
		start = 0
		yield 0
		while True:
			start = a_str.find(sub, start)
			if start == -1: return
			yield start
			start += len(sub) # use start += 1 to find overlapping matches

	def parseJSON(self, ff, sep):
		'''
			Receives a String and an array with the positions of \n in that
			string is located. Returns a JSON list.
		'''
		ndJson = []
		if len(sep) > 1:
			for i in range(len(sep)-1):
				pre = sep[i]
				post = sep[i+1]
				ndJson.append(json.loads(ff[pre:post]))
		else:
			ndJson.append(json.loads(ff))
		return ndJson

	# def numOfMeas(self):
	#     self.size = sum( [len(self.binariesRequestDict[i]['entry']) for i in range(len(self.resources))] )

	def saveJSON(self, obj, filename='FHIRdata.json'):
		dictJSON = json.dumps(obj)
		os.path.isdir(os.path.join(os.getcwd(), self.pathToDump)) or os.mkdir(os.path.join(os.getcwd(), self.pathToDump))
		f = open(os.path.join(os.getcwd(), self.pathToDump, filename),"w")
		f.write(dictJSON)
		f.close()
		self.logging.info(f'File {filename} saved to {os.path.join(os.getcwd(), self.pathToDump)}')

	def loadJSON(self, filename='FHIRdata.json'):
		with open(os.path.join(os.getcwd(), self.pathToDump, filename), 'r') as h:
			js = json.load(h)
		return js

	def logFunc(self):
		self.initTime = datetime.now()
		self.logging = logging
		os.path.isdir(os.path.join(os.getcwd(), self.pathToDump)) or os.mkdir(os.path.join(os.getcwd(), self.pathToDump))
		self.logging.basicConfig(filename=os.path.join(os.getcwd(), self.pathToDump, 'bulkExport.log'), level=logging.DEBUG)
		logging.info(f'{str(self.initTime).split(".")[0]} - Bulk Export started')
		self.logging.info(f'inOut - Data will be dumped in {self.pathToDump}')

	def initDict(self):
		self.resources = {}
		self.typeOfResources = np.unique([self.binariesRequestDict['output'][i]['type'] for i in range(len(self.binariesRequestDict['output']))]).tolist()
		for res in self.typeOfResources:
			self.resources[res] = []


if __name__ == '__main__':
	a = inOut("2021-05-28")


###################
# class inOut(object):
#     def __init__(self, path = "https://trustsphere.demo.smilecdr.com/fhir-request/Observation?code=440404000&subject=Patient/292046&date=lt2021-05-30T00:00:00Z&date=gt2021-05-15T00:00:00Z"):
#         self.resources = []
#         self.myRequest = requests.get(path)
#         # dict(self.myRequest.headers);
#         self.myDict =  json.loads(self.myRequest.text.replace("\n", "").replace(" ",""))
#
#         self.resources.append(self.myDict)
#         # resources[0]["link"][1]["relation"]
#         # self.getAll(MAX=10)
#         self.getAll()
#         # self.getDates()
#         # self.getCGM()
#         # self.sortData()
#         #
#         # self.numOfMeas()
#
#     def getAll(self, MAX=100):
#         for i in range(MAX):
#             if len(self.myDict["link"]) > 1:
#                 if self.myDict["link"][1]["relation"] == "next":
#                     self.myRequest = requests.get(self.myDict["link"][1]["url"])
#                     self.myDict =  json.loads(self.myRequest.text.replace("\n", "").replace(" ",""))
#                     self.resources.append(self.myDict)
#                     if i == MAX - 1 and self.myDict["link"][1]["relation"] == "next":
#                         print("Increase MAX")
#                 else:
#                     i=MAX
#         self.numOfMeas()
#     def numOfMeas(self):
#         self.size = sum( [len(self.resources[i]['entry']) for i in range(len(self.resources))] )
#
#     def saveJSON(self, filename='FHIRdata.json', path='FHIR/temp'):
#         dictJSON = json.dumps(self.resources)
#         f = open(os.path.join(os.getcwd(), path, filename),"w")
#         f.write(dictJSON)
#         f.close()
#
#     def loadJSON(self, filename='FHIRdata.json', path='FHIR/temp'):
#         with open(os.path.join(os.getcwd(), path, filename), 'r') as h:
#             js = json.load(h)
#         return js
#
#     # def getDate(self, x):
#     #     return datetime.fromisoformat(x[:-1])
#     #
#     # def getDates(self):
#     #     self.dates = [self.getDate(self.resources[i]['entry'][j]['resource']['effectiveDateTime']) for i in range(len(self.resources)) for j in range(len(self.resources[i]['entry']))]
#     #
#     # def getCGM(self):
#     #     self.CGM = [self.resources[i]['entry'][j]['resource']['valueQuantity']['value'] for i in range(len(self.resources)) for j in range(len(self.resources[i]['entry']))]
#     #
#     # def sortData(self):
#     #     idx = numpy.argsort(self.dates)
#     #     self.dates = [self.dates[i] for i in idx]
#     #     self.CGM = [self.CGM[i] for i in idx]


# class CGM(inOut):
#     def __init__(self, date = "2021-05-29"):
#         super(CGM, self).__init__(date = date)
#
#         self.getDates()
#         self.getCGM()
#         self.sortData()
#
#         # self.numOfMeas()
#
#     def getDate(self, x):
#         try:
#             return datetime.fromisoformat(x[:-1])
#         except:
#             return datetime.fromisoformat(x[:])
#     def getDates(self):
#         self.dates = [self.getDate(self.Obs[i]['effectiveDateTime']) for i in range(len(self.Obs))]
#
#     def getCGM(self):
#         self.CGM = [self.Obs[i]['valueQuantity']['value'] for i in range(len(self.Obs))]
#
#     def sortData(self):
#         idx = np.argsort(self.dates)
#         self.dates = [self.dates[i] for i in idx]
#         self.CGM = [self.CGM[i] for i in idx]
