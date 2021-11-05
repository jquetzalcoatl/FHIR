import requests
# from requests.auth import HTTPBasicAuth
import json
import numpy as np
import pandas as pd
from datetime import datetime
import time
import os
import logging
import sys
from utils.tokens import tokens as tok
###
# os.getcwd()
# os.chdir(os.path.join(os.getcwd(), "FHIR"))

# PATH = "https://trustsphere.demo.smilecdr.com/fhir-request/Observation?code=440404000&subject=Patient/292046&date=lt2021-05-30T00:00:00Z&date=gt2021-05-15T00:00:00Z"
# PATH = "https://trustsphere.demo.smilecdr.com/fhir-request/$export?_since=2021-05-29T00:00:00Z"
# requests.get('https://api.github.com/user', auth=('user', 'pass'))
# Making a get request
# response = requests.get('https://api.github.com / user, ', auth = HTTPBasicAuth('user', 'pass'))

# date = "2021-05-29"
# group_id="CONSENT-GIVEN-GROUP"
# path = "http://trustsphere.demo.smilecdr.com/fhir-request/Group/" + group_id + "/$export?_since=" + date + "T00:00:00Z"
# path = "http://trustsphere.demo.smilecdr.com/fhir-request" + "/$export?_since=" + date + "T00:00:00Z"
# BulkRequest = requests.get(path, headers={"Prefer" : "respond-async"})
# BulkRequestHeaderDict = dict(BulkRequest.headers)
# BulkRequestHeaderDict

class bulkImport(object):
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
		# self.Obs = []
		# self.Group = []
		# self.Meds = []
		# self.Patients = []
		# self.CodeSystem = []
		# self.Questionnaire = []
		# self.QuestionnaireResponse = []

		# PUT -> server consent w/o and participants
		self.logFunc()
		self.getBinaryLinks()
		if self.initDict():
			self.getAllBinaries(MAX=MAX)
			self.logging.info('bulkImport - Binaries Loaded!')

	def getBinaryLinks(self):
		# self.BulkRequest = requests.get(self.path, headers={"Prefer" : "respond-async"})
		self.BulkRequest = requests.get(self.path, headers={"Prefer" : "respond-async"}, auth=(tok["username"], tok["pwd"]))
		self.BulkRequestHeaderDict = dict(self.BulkRequest.headers)
		self.binariesRequest = requests.get(self.BulkRequestHeaderDict['Content-Location'])

		try:
			while dict(self.binariesRequest.headers)['Retry-After'] == '120':
				self.logging.info('bulkImport - Binaries not ready yet...sleep 120s')
				time.sleep(120)
				self.binariesRequest = requests.get(self.BulkRequestHeaderDict['Content-Location'])
		except:
			self.logging.info("bulkImport - Binary Links are ready")

		self.binariesRequestDict = json.loads(self.binariesRequest.text.replace("\n", "").replace(" ",""))

		self.saveJSON(self.BulkRequestHeaderDict, f'BulkRequestHeaderDict.json')
		self.logging.info("bulkImport - BulkRequestHeaderDict object saved")
		self.saveJSON(self.binariesRequestDict, f'binariesRequestDict.json')
		self.logging.info("bulkImport - binariesRequestDict object saved")

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
				sep.append(len(temp.text))
				typeRes = self.binariesRequestDict['output'][i]['type']
				self.resources[typeRes] = self.resources[typeRes] + self.parseJSON(temp.text,sep)

			except:
				self.logging.warning(f'bulkImport - Binary with index {i} was not loaded.')

		# self.typeOfResources = list(np.unique([self.binariesRequestDict['output'][i]['type'] for i in range(len(self.binariesRequestDict['output']))]))
		self.logging.info(f'type of resources: {self.typeOfResources}')
		self.logging.info(f'bulkImport - \n')
		for key in self.resources.keys():
			m = len(self.resources[key])
			self.logging.info(f'Number of {key} resources = {m} \n')
			if m > 0:
				self.saveJSON(self.resources[key], f'{key}.json')
				self.logging.info(f'bulkImport - {key} resource object saved')

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
		'''
			https://stackoverflow.com/questions/24816456/python-logging-wont-shutdown
		'''
		self.initTime = datetime.now()
		os.path.isdir(os.path.join(os.getcwd(), self.pathToDump)) or os.mkdir(os.path.join(os.getcwd(), self.pathToDump))

		self.logging = logging
		self.logging = logging.getLogger()
		self.logging.setLevel(logging.DEBUG)
		self.handler = logging.FileHandler(os.path.join(os.getcwd(), self.pathToDump, 'bulkExport.log'))
		self.handler.setLevel(logging.DEBUG)
		formatter = logging.Formatter(
		            fmt='%(asctime)s %(levelname)s: %(message)s',
		            datefmt='%Y-%m-%d %H:%M:%S'
		            )
		self.handler.setFormatter(formatter)
		self.logging.addHandler(self.handler)

		self.logging.info(f'{str(self.initTime).split(".")[0]} - Bulk Export started')
		self.logging.info(f'bulkImport - Data will be dumped in {self.pathToDump}')
		# self.logging.removeHandler(self.handler) #To close

	def initDict(self):
		self.resources = {}
		try:
			self.typeOfResources = np.unique([self.binariesRequestDict['output'][i]['type'] for i in range(len(self.binariesRequestDict['output']))]).tolist()
			for res in self.typeOfResources:
				self.resources[res] = []
			return True
		except:
			self.logging.error(f'No new data in that time window. Check the output field in binariesRequestDict.json which seems to be missing')
			# sys.exit(1) # Uncomment this for code to halt when no data is available.
			return False


if __name__ == '__main__':
	a = bulkImport("2021-05-28")
