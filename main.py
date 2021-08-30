from utils.observations import ObsDF
import argparse
import os
from datetime import datetime
import logging


# os.getcwd()
# os.chdir(os.path.join(os.getcwd(), "FHIR"))
# df = pd.read_csv("/Users/javier/Desktop/Python/FHIR/temp-2021-06-10/Observations.csv")

# import json
# def loadJSON(filename='/Users/javier/Desktop/Python/FHIR/TS-BulkExport-2021-07-29/binariesRequestDict.json'):
# def loadJSON(filename="/Users/javier/Desktop/Python/FHIR/TS-BulkExport-2021-07-29/MedicationAdministration.json"):
# def loadJSON(filename="/Users/javier/Desktop/Python/FHIR/TS-BulkExport-2021-07-29/Observation.json"):
# def loadJSON(filename="/Users/javier/Desktop/Python/FHIR/TS-BulkExport-2021-08-30/QuestionnaireResponse.json"):
# 	with open(filename, 'r') as h:
# 		js = json.load(h)
# 	return js
#
#
# #
# jsonObj1 = loadJSON()
# jsonObj1[2]
# [jsonObj1[i]['id'] for i in range(9)]
# [jsonObj1[i]['meta']['lastUpdated'] for i in range(9)]
# [jsonObj1[i]['questionnaire'] for i in range(9)]
# sum([jsonObj1[i]['id'] == '44655829-5b03-4feb-9f32-eaad89077e0e-1' for i in range(len(jsonObj1))])
# for i in range(len(jsonObj1)):
# 	if jsonObj1[i]['id'] == '44655829-5b03-4feb-9f32-eaad89077e0e-2':
# 		print(i)
# 		break
# jsonObj1[906]
# jsonObj1[757]
#
# jsonObj1[3]
# jsonObj[0]
# import numpy as np
# np.unique([jsonObj['output'][i]['type'] for i in range(len(jsonObj['output']))]).tolist()

# r = stats(date="2021-06-21", MAX=10)
# import numpy as np
# len(r.Obs)
# r.Obs[100]
# # r.Questionnaire
# r.dfQuestionnaire

if __name__ == '__main__':
	print(f'Main - Current directory: {os.getcwd()}')
	parser = argparse.ArgumentParser("Add date in yyyy-mm-dd format")
	parser.add_argument('--date', dest="date", type=str, default="2021-04-21",
						help='Specify date since tag for FHIR bulk export. \n Default set to 2021-04-21')
	parser.add_argument('--max', dest="max", type=int, default=0,
						help='Specify number of binaries. \n Default set to 5')
	args = parser.parse_args()
	print(f'Main - Data transfer since {args.date} starting...')
	print(f'Date selected: {args.date}. Max number of binaries set to {args.max}')
	# r = stats(date=args.date, MAX=args.max)
	r = ObsDF(date=args.date, MAX=args.max)
	r.logging.info(f'Bulk Export ended after t = {str(datetime.now() - r.initTime)}')
	r.logging.info(f'#############################################################################################')
	r.logging.removeHandler(r.handler)
	# os.system(f'streamlit run visualization.py -- --date {str(datetime.now()).split(" ")[0]}')
	# !streamlit run visualization.py -- --date str(datetime.now()).split(" ")[0]
