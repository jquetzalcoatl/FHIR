import numpy as np

class BGRiskAssesment(object):
	'''
		Clarke W, Kovatchev B. Statistical Tools to Analyze Continuous Glucose Monitor Data.
        Diabetes Technology & Therapeutics. 2009; 11(Suppl 1): S-45-S-54.
        doi:10.1089/dia.2008.0138.
	'''
	def __init__(self, cgm):
		self.cgm = cgm
		# self.f = lambda x : 1.509 * ((np.log(x))**1.084 - 5.381) # if in mg/dL
		self.f = lambda x : 1.509 * ( np.real(np.power(np.log(x + 0.0001), 1.084, dtype=np.complex128)) - 5.381)
		# f(BG, c::Bool) = 1.509 * (log(18 * BG)^1.084 - 5.381) # if in mmol/L
		self.r = lambda x : 10 * (x)**2
		self.LBGI = np.mean([self.r(min(self.f(self.cgm.iloc[i]),0)) for i in range(len(self.cgm))])
		self.HBGI = np.mean([self.r(max(self.f(self.cgm.iloc[i]),0)) for i in range(len(self.cgm))])
	def LBGRisk(self):

		if self.LBGI <= 1.1:
			return "Minimal"
		elif 1.1 < self.LBGI <=2.5:
			return "Low"
		elif 2.5 < self.LBGI <= 5:
			return "Moderate"
		elif self.LBGI > 5.0:
			return "High"
