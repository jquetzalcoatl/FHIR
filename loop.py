from utils.observations import ObsDF
from utils.dataAnalysis import dataObject
import argparse
import os
from datetime import datetime, date, timedelta
import time
import logging

# os.getcwd()
# os.chdir(os.path.join(os.getcwd(), "FHIR"))

if __name__ == '__main__':
	while True:
		print(f'Main - Current directory: {os.getcwd()}')
		since = str(datetime.today() - timedelta(days=1)).split(" ")[0]
		print(f'Main - Data transfer since {since} starting...')

		r = ObsDF(date=since, MAX=0)
		r.logging.info(f'Bulk Export ended after t = {str(datetime.now() - r.initTime)}')
		r.logging.info(f'#############################################################################################')
		r.logging.removeHandler(r.handler)
		b = dataObject(since=since, aggregate=True)
		time.sleep(120) #Sleep 2*24hrs = 2 * 86400
	# os.system(f'streamlit run visualization.py -- --date {str(datetime.now()).split(" ")[0]}')
	# !streamlit run visualization.py -- --date str(datetime.now()).split(" ")[0]
