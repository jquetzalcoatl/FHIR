from utils.observations import ObsDF
from utils.BGriskAssesment import BGRiskAssesment
import pandas as pd
import os
from datetime import datetime
import numpy as np

class stats(ObsDF):
	def __init__(self, obs=0, date = "2021-05-29", MAX=3, ptId=0, dateStart=0, dateEnd=0, thrsUL=55, thrsBR=80, thrsAR=200):
		if obs == 0:
			super(stats, self).__init__(date = date, MAX=MAX)
		else:
			self.Obs = obs[0]
			self.df = obs[1]

		self.getDates()
		self.getCGM()
		self.getPatients()
		self.sortData()
		self.createTable()

		self.getWindow(ptId, dateStart, dateEnd)
		self.BGRiskAssesment = BGRiskAssesment(self.reducedDF['CGM'])
		self.getStats(thrsUL, thrsBR, thrsAR)

		if obs == 0:
			self.saveJSON(self.statDict, f'statDict.json')

	def getDate(self, x):
			try:
				return datetime.fromisoformat(x[:-1])
			except:
				return datetime.fromisoformat(x[:])

	def getDates(self):
		self.dates = [self.getDate(self.Obs[i]['effectiveDateTime']) for i in range(len(self.Obs)) ]

	def getCGM(self):
		self.CGM = [self.Obs[i]['valueQuantity']['value'] for i in range(len(self.Obs)) ]

	def getPatients(self):
		self.Pts = [self.Obs[i]['subject']['reference'] for i in range(len(self.Obs)) ]

	def sortData(self):
		idx = np.argsort(self.dates)
		self.dates = [self.dates[i] for i in idx]
		self.CGM = [self.CGM[i] for i in idx]
		self.Pts = [self.Pts[i] for i in idx]

	def createTable(self):
		self.df2 = pd.DataFrame(index=range(len(self.CGM)), columns=['Patients', 'CGM', 'Dates'])
		self.df2['Patients'] = self.Pts
		self.df2['CGM'] = self.CGM
		self.df2['Dates'] = self.dates

	def getWindow(self, ptId=0, dateStart=0, dateEnd=0):
		if ptId == 0:
			q1 = pd.DataFrame([True for i in range(len(self.CGM))])[0]
		else:
			q1 = self.df2['Patients'] == ptId
		if dateStart == 0:
			q2 = pd.DataFrame([True for i in range(len(self.CGM))])[0]
		else:
			q2 = self.df2['Dates'] >= self.getDate(dateStart)
		if dateEnd == 0:
			q3 = pd.DataFrame([True for i in range(len(self.CGM))])[0]
		else:
			q3 = self.df2['Dates'] <= self.getDate(dateEnd)

		self.reducedDF = self.df2[q1 & q2 & q3]

	def getWindow2(self, ptId=0, dateStart=0, dateEnd=0):
		if ptId == 0:
			q1 = pd.DataFrame([True for i in range(len(self.CGM))])[0]
		else:
			q1 = self.df2['Patients'] == ptId
		if dateStart == 0:
			q2 = pd.DataFrame([True for i in range(len(self.CGM))])[0]
		else:
			q2 = self.df2['Dates'] >= dateStart
		if dateEnd == 0:
			q3 = pd.DataFrame([True for i in range(len(self.CGM))])[0]
		else:
			q3 = self.df2['Dates'] <= dateEnd

		self.reducedDF = self.df2[q1 & q2 & q3]

	def getStats(self, thrsUL=55, thrsBR=80, thrsAR=200):
		self.statDict ={
			'mean' : str(round(np.mean(self.reducedDF['CGM']),3)),
			'median' : str(np.median(self.reducedDF['CGM'])),
			'min' : str(np.min(self.reducedDF['CGM'])),
			'max' : str(np.max(self.reducedDF['CGM'])),
			'var' : str(np.var(self.reducedDF['CGM'])),
			'std' : str(np.std(self.reducedDF['CGM'])),
			'sum' : str(np.sum(self.reducedDF['CGM'])),
			'q25' : str(np.percentile(self.reducedDF['CGM'], 25)),
			'q50' : str(np.percentile(self.reducedDF['CGM'], 50)),
			'q75' : str(np.percentile(self.reducedDF['CGM'], 75)),
			'utilizationPerc' : str(len(self.reducedDF['CGM'])/( (self.reducedDF['Dates'].iloc[-1] - self.reducedDF['Dates'].iloc[0]).total_seconds()/60 * 1/5 + 1 )),
			'hypoRisk' : self.BGRiskAssesment.LBGRisk(),
			'LowBGIndex' : str(self.BGRiskAssesment.LBGI),
			'HighBGIndex' : str(self.BGRiskAssesment.HBGI),
			'nDays' : str(int(np.floor( (self.reducedDF['Dates'].iloc[-1] - self.reducedDF['Dates'].iloc[0]).total_seconds()/3600 * 1/24 + 1 ))),
			'nValues' : str(len(self.reducedDF['CGM'])),
			'nUrgentLow' : str(sum(self.reducedDF['CGM'] < thrsUL)),
			'nBelowRange' : str(sum((self.reducedDF['CGM'] >= thrsUL) & (self.reducedDF['CGM'] < thrsBR))),
			'nInRange' : str(sum((self.reducedDF['CGM'] >= thrsBR) & (self.reducedDF['CGM'] < thrsAR))),
			'nAboveRange' : str(sum(self.reducedDF['CGM'] >= thrsAR)),
			'PerUrgentLow' : str(sum(self.reducedDF['CGM'] < thrsUL)/len(self.reducedDF['CGM'])),
			'PerBelowRange' : str(sum((self.reducedDF['CGM'] >= thrsUL) & (self.reducedDF['CGM'] < thrsBR))/len(self.reducedDF['CGM'])),
			'PerInRange' : str(sum((self.reducedDF['CGM'] >= thrsBR) & (self.reducedDF['CGM'] < thrsAR))/len(self.reducedDF['CGM'])),
			'PerAboveRange' : str(sum(self.reducedDF['CGM'] >= thrsAR)/len(self.reducedDF['CGM'])),
			'CoeffVariation' : str(np.std(self.reducedDF['CGM'])/np.mean(self.reducedDF['CGM'])),
			}

if __name__ == '__main__':
    stats("2021-06-01")
