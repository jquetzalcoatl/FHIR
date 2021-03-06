from utils.resources import resources
from utils.concatenate import concat
import argparse
import os
from datetime import datetime, date, timedelta
import time
import logging

# os.getcwd()
# os.chdir(os.path.join(os.getcwd(), "FHIR"))
# nohup python3 loop.py &

if __name__ == '__main__':
	while True:
		# print(f'Main - Current directory: {os.getcwd()}')
		since = str(datetime.today() - timedelta(days=5)).split(" ")[0]
		# print(f'Main - Data transfer since {since} starting...')

		r = resources(date=since, MAX=0)
		r.logging.info(f'Bulk Export ended after t = {str(datetime.now() - r.initTime)}')
		r.logging.info(f'#############################################################################################')
		r.logging.removeHandler(r.handler)
		b = concat(since=since, concatenate=True)
		time.sleep(36000) #Sleep 10 hrs.  2*24hrs = 2 * 86400
	# os.system(f'streamlit run visualization.py -- --date {str(datetime.now()).split(" ")[0]}')
	# !streamlit run visualization.py -- --date str(datetime.now()).split(" ")[0]
