import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from datetime import datetime, date
import seaborn as sns
import altair as alt
import argparse
import os
import base64
import sys

from pathlib import Path
print(Path(os.getcwd()).parent.absolute())
sys.path.insert(1, os.path.join(Path(os.getcwd()).parent.absolute(), 'utils'))
# sys.path.insert(1, '/app/fhir/')
# sys.path.insert(1, '../')


# ##
# os.getcwd()
# os.chdir(os.path.join(os.getcwd(),  "FHIR", "dashboard"))
# from utils.load_css import local_css, textFunc, statsTextFunc
# from utils.dataQueryVis import dataQuery, Stat
# from utils.dataTuples import codes
from load_css import local_css, textFunc, statsTextFunc
from dataQueryVis import dataQuery, Stat
from dataTuples import codes
alt.data_transformers.disable_max_rows()


# $streamlit run visualization.py -- --date 2021-09-22
# https://github.com/streamlit/streamlit/issues/337#issuecomment-544860528

#PARSING
parser = argparse.ArgumentParser(description='This app shows CGM')

parser.add_argument('--date', dest="date", type=str, default="2021-09-22",
					help='Specify date since tag for FHIR bulk export. \n Default set to 2021-07-05')

try:
	args = parser.parse_args()
except SystemExit as e:
	# This exception will be raised if --help or invalid command line arguments
	# are used. Currently streamlit prevents the program from exiting normally
	# so we have to do a hard exit.
	os._exit(e.code)



# a = dataQuery(date="2021-09-22")
# a.metadata['Patients'].append('All')

#Dashboard
# can only set this once, first thing to set
apptitle = 'TS-Registry Dashboard'
st.set_page_config(page_title=apptitle, layout="wide")
local_css(os.path.join(Path(os.getcwd()).parent.absolute(), "utils", "style.css"))

with st.container():
	st.title("TS-Registry Visualization Tool")
	st.header(f'(Showing dummy data from {args.date} bulk export!)')
	st.write(f'{os.getcwd()}')

@st.cache(allow_output_mutation=True)
def loadData():
	return dataQuery(date=args.date)
a = loadData()
# a.metadata['Patients'].append('All')

option = st.sidebar.selectbox("Select Dashboard", ("Patient Level", "Aggregated Level"))

if option == "Patient Level":
	alpha = 1.0
	with st.sidebar:
		x = st.radio("Select units:", ("mg/dL", "mmol/L"))
		if x == "mmol/L":
			st.warning('Measurements are done in mg/dL and then converted to mmol/L.')
		# st.write(x)
		with st.expander("Choose Patient", expanded = True):
			chart_type = st.selectbox("", a.metadata['Patients'])
		# with st.expander("Choose Kind of Data"):
		# 	data_type = st.selectbox("", [a.PtDF[chart_type][key]['display'] for key in a.PtDF[chart_type].keys() ])
	if x == "mmol/L":
		alpha = 1.0/18.0
	elif x == "mg/dL":
		alpha = 1.0

	a.getWindow(ptId=chart_type, dateStart=0, dateEnd=0)
	# a.reducedDF.keys()
	# a.reducedDF['440404000']['df'].info()
	# a.reducedDF['440404000']['df']['root-component-component_2-valueString']


	def update_timeSliderLeft():
			# st.session_state.timeSlider = (datetime.combine(st.session_state.calendar1, datetime.min.time()), datetime.combine(st.session_state.calendar2, datetime.min.time()))
		st.session_state.timeSlider = (datetime.combine(st.session_state.calendar1, datetime.min.time()), st.session_state.timeSlider[1])

	def update_timeSliderRight():
		st.session_state.timeSlider = (st.session_state.timeSlider[0], datetime.combine(st.session_state.calendar2, datetime.min.time()) )

	# a.getDate(str(a.reducedDF['Dates'].iloc[-1])).time()
	# datetime.min.time()
	# min(a.getDate(str(a.reducedDF['Dates'].iloc[-1])), a.getDate(str(a.reducedDF['Dates'].iloc[1])))
	# min(datetime.min.time(), datetime.max.time())
	# with row1_2:
	with st.container():
		st.title("Time Window")
		hour_selected0 = (a.getDate(str(a.reducedDF[codes['CGM']]['df']['Dates'].iloc[0])), a.getDate(str(a.reducedDF[codes['CGM']]['df']['Dates'].iloc[-1])))
		hour_selected = st.slider("Select Time Window", key='timeSlider', value=hour_selected0, min_value=hour_selected0[0], max_value=hour_selected0[1])

	#####
	row1_1, row1_2 = st.columns((2,2))
	with row1_1:
		hour_s0 = st.date_input("Start date", value = hour_selected[0], key='calendar1', min_value=hour_selected0[0], max_value=hour_selected0[1], on_change=update_timeSliderLeft)

	with row1_2:
		hour_s1 = st.date_input("End date", value = hour_selected[1], key='calendar2', min_value=hour_selected0[0], max_value=hour_selected0[1], on_change=update_timeSliderRight)
	############

	# utc=pytz.UTC
	# hour_selected[0]
	# chart_type
	# hour_selected[0].replace(tzinfo=utc)
	# a.ObsDF['Dates'].apply(lambda x: x.replace(tzinfo=utc)) > hour_selected[0].replace(tzinfo=utc)
		# hour_selected[0]
		# a.PtDF.keys()
		# a.PtDF['Patient/2023']['440404000']['df']['Dates']
		# a.PtDF['Patient/405878']['39543009']['df']['Dates'].astype(object)# >= hour_selected[0].replace(tzinfo=utc)
		# a.PtDF[ptId][key]['df']['Dates']
	# print(hour_selected[0], "    ", hour_selected[1])
	a.getWindow3(ptId=chart_type, dateStart=hour_selected[0], dateEnd=hour_selected[1])
	thrsUL=54
	thrsBR=72
	thrsAR=198
	# a.getStats(thrsUL=55, thrsBR=80, thrsAR=200)
	# a.reducedDF.columns

	with st.sidebar:
		# show_params = st.checkbox("Set thresholds", False)
		# if show_params:
		with st.expander("Set thresholds", expanded = True):
			thrsUL = st.slider("Select urgently low threshold", min_value=0.0, max_value = 396 * alpha, value=54 * alpha, step = alpha)
			thrsBR = st.slider("Select below range threshold", min_value=thrsUL+1 * alpha, max_value = 396 * alpha, value=thrsUL+18 * alpha, step = alpha)
			thrsAR = st.slider("Select above range threshold", min_value=thrsBR+1 * alpha, max_value = 396 * alpha, value=thrsBR+126 * alpha, step = alpha)
	a.getStats(thrsUL=thrsUL * 1/alpha, thrsBR=thrsBR * 1/alpha, thrsAR=thrsAR * 1/alpha)
	with st.container():
		# show_params = st.checkbox("Set thresholds", False)
		# if show_params:
		# 	thrsUL = st.slider("Select urgently low threshold", min_value=0, max_value = 400, value=55)
		# 	thrsBR = st.slider("Select below range threshold", min_value=thrsUL+1, max_value = 400, value=thrsUL+25)
		# 	thrsAR = st.slider("Select above range threshold", min_value=thrsBR+1, max_value = 400, value=thrsBR+120)
		st.subheader(f"Displaying:  {chart_type}  (F)")
		st.write("")

		# st.markdown(textFunc("mean",a.statDict["mean"]), unsafe_allow_html=True)
		# st.button("Here")
		if x == "mg/dL":
			# st.write(a.statDict)
			st.markdown(statsTextFunc(a.statDict), unsafe_allow_html=True)
		else:
			st.markdown(statsTextFunc(a.statDict2), unsafe_allow_html=True)


	def coloring(x, thrsUL=55, thrsBR=80, thrsAR=200):
		if x < thrsUL:
			return 'red'
		elif x < thrsBR:
			return 'orange'
		elif x < thrsAR:
			return 'green'
		else:
			return 'red'

	def plotGMIPred(x0, dx=3.0, step=0.1, sd=0.784):
		GMIPred =pd.DataFrame(data = {"GMI" : [x for x in np.arange(x0-dx,x0+dx,step)], "Probability" : [1/np.sqrt(2*np.pi*np.power(sd, 2)) * np.exp(-np.power(x-x0,2)/(2*np.power(sd, 2))) for x in np.arange(x0-dx,x0+dx,step)]})
		st.write("Probabilistic GMI") #.mark_line(point=True, strokeWidth=3, color='#e377c2')
		c = alt.Chart(GMIPred).mark_area(color='#e377c2').encode(alt.X('GMI', axis=alt.Axis(labelAngle=-0), scale=alt.Scale(zero=False)), alt.Y('Probability', scale=alt.Scale(zero=False)), tooltip=['GMI', 'Probability']).properties(width=800, height=400).interactive().configure_point(size=200, color='#e377c2')
		st.write(c)
	# a.reducedDF['CGM (mmol/L)']
	# create plots
	# alt.data_transformers.disable_max_rows()
	def show_plot(kind: str):
		reducedDF = {}

		try:
			reducedDF[codes['CGM']] = a.reducedDF[codes['CGM']]['df'][['Dates', 'CGM', 'Patients', 'CGM (mmol/L)']].reset_index()
			reducedDF[codes['CGM']]['CGM (mg/dL)'] = reducedDF[codes['CGM']]['CGM']
			reducedDF[codes['CGM']]["Dates"] = pd.to_datetime(reducedDF[codes['CGM']]['Dates'])
		except:
			return st.write("No CGM data.")

		if kind == "insulin":
			try:
				reducedDF[codes['Insulin']] = a.reducedDF[codes['Insulin']]['df'][['Dates', 'Insulin', 'Patients']].reset_index()
				# reducedDF[codes['Insulin']]['Insulin (units)'] = reducedDF[codes['CGM']]['CGM']
				reducedDF[codes['Insulin']]["Dates"] = pd.to_datetime(reducedDF[codes['Insulin']]['Dates'])
			except:
				return st.write("No insulin data.")

		if kind == "intake":
			try:
				reducedDF[codes['CarbIntake']] = a.reducedDF[codes['CarbIntake']]['df'][['Dates', 'CarbIntake', 'Patients']].reset_index()
				reducedDF[codes['CarbIntake']]['Carbs Intake (grams)'] = reducedDF[codes['CarbIntake']]['CarbIntake']
				reducedDF[codes['CarbIntake']]["Dates"] = pd.to_datetime(reducedDF[codes['CarbIntake']]['Dates'])
			except:
				return st.write("No Carb intake data.")



		if kind == "CGM time series":
			fig, ax = plt.subplots()
			ax.set_xticklabels(reducedDF[codes['CGM']]['Dates'], rotation=45)
			ax.set_xlabel("Date")
			ax.set_ylabel(f'CGM ({x})')
			ll = reducedDF.shape[0]
			ax.plot(reducedDF['Dates'], reducedDF['CGM'], c='black', linewidth=0.05)#matplotlib_plot(chart_type, df)
			ax.scatter(reducedDF['Dates'], reducedDF['CGM'])
			ax.plot(reducedDF['Dates'], [thrsUL for i in reducedDF['Dates']], c='r')
			ax.plot(reducedDF['Dates'], [thrsBR for i in reducedDF['Dates']], c='y')
			ax.plot(reducedDF['Dates'], [thrsAR for i in reducedDF['Dates']], c='purple')
			st.pyplot(fig)
		elif kind == "CGM time series 2":
			fig, ax = plt.subplots()
			ax.set_xticklabels(reducedDF['Dates'], rotation=45)
			ax.set_xlabel("Date")
			ax.set_ylabel(f'CGM ({x})')
			ll = reducedDF.shape[0]
			ax.plot(reducedDF['Dates'], reducedDF['CGM (mmol/L)'], c='black', linewidth=0.05)#matplotlib_plot(chart_type, df)
			ax.scatter(reducedDF['Dates'], reducedDF['CGM (mmol/L)'])
			ax.plot(reducedDF['Dates'], [thrsUL for i in reducedDF['Dates']], c='r')
			ax.plot(reducedDF['Dates'], [thrsBR for i in reducedDF['Dates']], c='y')
			ax.plot(reducedDF['Dates'], [thrsAR for i in reducedDF['Dates']], c='purple')
			st.pyplot(fig)
		elif kind == "CGM Histogram":
			fig, ax = plt.subplots(figsize=(10, 10))
			# sns.set(rc={'figure.figsize':(11.7,8.27)})
			b = st.slider("Select number of bins", min_value=1, max_value = 100, value=10)
			sns.histplot(reducedDF[codes['CGM']]['CGM'], ax=ax, kde=True, bins=b, stat="density", element="step")
			st.pyplot(fig)
		elif kind == "CGM Histogram 2":
			fig, ax = plt.subplots(figsize=(10, 10))
			b = st.slider("Select number of bins", min_value=1, max_value = 100, value=10)
			sns.histplot(reducedDF[codes['CGM']]['CGM (mmol/L)'], ax=ax, kde=True, bins=b, stat="density", element="step")
			st.pyplot(fig)
		elif kind == "altair":
			st.write(a.reducedDF[codes['CGM']]['display'])#mark_circle()
			c = alt.Chart(reducedDF[codes['CGM']]).mark_line(point=True, strokeWidth=3).encode(alt.X('Dates', axis=alt.Axis(labelAngle=-30), scale=alt.Scale(zero=False)), alt.Y('CGM (mg/dL)', scale=alt.Scale(zero=False)), alt.Text('Patients'), tooltip=['Patients', 'Dates', 'CGM (mg/dL)']).properties(width=800, height=400).interactive()
			linethrsUL = alt.Chart(pd.DataFrame({'CGM (mg/dL)': [thrsUL]})).mark_rule().encode(y='CGM (mg/dL)')
			linethrsBR = alt.Chart(pd.DataFrame({'CGM (mg/dL)': [thrsBR]})).mark_rule().encode(y='CGM (mg/dL)')
			linethrsAR = alt.Chart(pd.DataFrame({'CGM (mg/dL)': [thrsAR]})).mark_rule().encode(y='CGM (mg/dL)')
			st.write(alt.layer(c + linethrsUL + linethrsBR + linethrsAR).configure_point(size=50))
		elif kind == "altair 2":
			st.write(a.reducedDF[codes['CGM']]['display'])
			# reducedDF = a.reducedDF[['Dates', 'CGM (mmol/L)', 'Patients']].reset_index()
			# reducedDF["Dates"] = pd.to_datetime(reducedDF['Dates'])
			c = alt.Chart(reducedDF[codes['CGM']]).mark_line(point=True, strokeWidth=3).encode(alt.X('Dates', axis=alt.Axis(labelAngle=-30), scale=alt.Scale(zero=False)), alt.Y('CGM (mmol/L)', scale=alt.Scale(zero=False)), tooltip=['Patients', 'Dates', 'CGM (mmol/L)']).properties(width=800, height=400).interactive()
			linethrsUL = alt.Chart(pd.DataFrame({'CGM (mmol/L)': [thrsUL]})).mark_rule().encode(y='CGM (mmol/L)')
			linethrsBR = alt.Chart(pd.DataFrame({'CGM (mmol/L)': [thrsBR]})).mark_rule().encode(y='CGM (mmol/L)')
			linethrsAR = alt.Chart(pd.DataFrame({'CGM (mmol/L)': [thrsAR]})).mark_rule().encode(y='CGM (mmol/L)')
			# st.write(c + linethrsUL + linethrsBR + linethrsAR)
			st.write(alt.layer(c + linethrsUL + linethrsBR + linethrsAR).configure_point(size=50))
		elif kind == "insulin":
			st.write(a.reducedDF[codes['Insulin']]['display'])
			c = alt.Chart(reducedDF[codes['Insulin']]).mark_line(interpolate='step-after', color='#9467bd', strokeWidth=3).encode(alt.X('Dates', axis=alt.Axis(labelAngle=-30), scale=alt.Scale(zero=False)), alt.Y('Insulin', scale=alt.Scale(zero=False)), alt.Text('Patients'), tooltip=['Patients', 'Dates', 'Insulin']).properties(width=800, height=400).interactive().configure_point( size=200, color='#9467bd')
			st.write(c)
		elif kind == "intake":
			st.write(a.reducedDF[codes['CarbIntake']]['display'])
			c = alt.Chart(reducedDF[codes['CarbIntake']]).mark_line(point=True, strokeWidth=3, color='#e377c2').encode(alt.X('Dates', axis=alt.Axis(labelAngle=-30), scale=alt.Scale(zero=False)), alt.Y('Carbs Intake (grams)', scale=alt.Scale(zero=False)), tooltip=['Patients', 'Dates', 'Carbs Intake (grams)']).properties(width=800, height=400).interactive().configure_point(size=200, color='#e377c2')
			st.write(c)
		elif kind == "allIn":
			st.write(a.reducedDF[codes['CGM']]['display'])
			c = alt.Chart(reducedDF[codes['CGM']]).mark_line(point=False).encode(alt.X('Dates', axis=alt.Axis(labelAngle=0), scale=alt.Scale(zero=False)), alt.Y('CGM (mg/dL)', scale=alt.Scale(zero=False)), alt.Text('Patients'), tooltip=['Patients', 'Dates', 'CGM (mg/dL)']).properties(width=800, height=400).interactive()
			linethrsUL = alt.Chart(pd.DataFrame({'CGM (mg/dL)': [thrsUL]})).mark_rule().encode(y='CGM (mg/dL)')
			linethrsBR = alt.Chart(pd.DataFrame({'CGM (mg/dL)': [thrsBR]})).mark_rule().encode(y='CGM (mg/dL)')
			linethrsAR = alt.Chart(pd.DataFrame({'CGM (mg/dL)': [thrsAR]})).mark_rule().encode(y='CGM (mg/dL)')
			b = alt.Chart(reducedDF[codes['Insulin']]).mark_line(point=True, color='#57A44C').encode(alt.X('Dates', axis=alt.Axis(labelAngle=0), scale=alt.Scale(zero=False)), alt.Y('Insulin', scale=alt.Scale(zero=False)), alt.Text('Patients'), tooltip=['Patients', 'Dates', 'Insulin']).properties(width=800, height=400).interactive()
			# st.write(c + linethrsUL + linethrsBR + linethrsAR)
			# st.write(alt.layer(c, b).resolve_scale(y = 'independent'))
			st.write(alt.layer(c + linethrsUL + linethrsBR + linethrsAR, b).resolve_scale(y = 'independent'))
		# elif kind == "aggregated":
		# 	# df = pd.DataFrame(np.random.randn(200, 3),columns=['a', 'b', 'c'])
		# 	c = alt.Chart(a.ObsDF).mark_line(point=True).encode(alt.X('Dates', axis=alt.Axis(labelAngle=-45), scale=alt.Scale(zero=False)), alt.Y('CGM', scale=alt.Scale(zero=False)), alt.Color('Patients', legend=None, scale=alt.Scale(domain=a.metadata['Patients'],type='ordinal')), tooltip=['Patients', 'Dates', 'CGM']).properties(width=800, height=400).interactive()
		#
		# 	labels = alt.Chart(a.ObsDF).mark_text(align='left', dx=3, fontSize=15).encode(alt.X('Dates', aggregate='max', axis=alt.Axis(labelAngle=-45), scale=alt.Scale(zero=False)), alt.Y('CGM', aggregate={'argmax': 'Dates'}, scale=alt.Scale(zero=False)), alt.Text('Patients'), alt.Color('Patients', legend=None, scale=alt.Scale(domain=a.metadata['Patients'],type='ordinal')))
		#
		# 	linethrsUL = alt.Chart(pd.DataFrame({'CGM': [thrsUL]})).mark_rule().encode(y='CGM')
		# 	linethrsBR = alt.Chart(pd.DataFrame({'CGM': [thrsBR]})).mark_rule().encode(y='CGM')
		# 	linethrsAR = alt.Chart(pd.DataFrame({'CGM': [thrsAR]})).mark_rule().encode(y='CGM')
		# 	st.write(c + labels + linethrsUL + linethrsBR + linethrsAR)

	# a.reducedDF['39543009']['display']
	# a.reducedDF['9059-7']['df']
	# a.reducedDF['9059-7']['df']['root-valueQuantity-value']

	# np.unique(a.reducedDF['9059-7']['df']['root-valueQuantity-code']).tolist()[0]
	# a.reducedDF['39543009']['df'].columns


	# output plots
	with st.container():
		if x == "mg/dL":
			show_plot(kind="altair")
			show_plot(kind="insulin")
			show_plot(kind="intake")
			plotGMIPred(float(a.statDict["GMI"]))
			# show_plot(kind="allIn")
			# show_plot(kind="CGM time series")
			row1_1, row1_2 = st.columns((2,2))
			with row1_1:
				show_plot(kind="CGM Histogram")
		else:
			show_plot(kind="altair 2")
			show_plot(kind="insulin")
			show_plot(kind="intake")
			plotGMIPred(float(a.statDict["GMI"]))
			# show_plot(kind="CGM time series 2")
			row1_1, row1_2 = st.columns((2,2))
			with row1_1:
				show_plot(kind="CGM Histogram 2")


	# ss = a.reducedDF[['Dates', 'CGM', 'Patients']].reset_index()
	# ss["Dates"] = pd.to_datetime(ss['Dates'])
	# c = alt.Chart(ss.iloc[1:10,:]).mark_line(point=False).encode(alt.X('Dates', axis=alt.Axis(labelAngle=0), scale=alt.Scale(zero=False)), alt.Y('CGM', scale=alt.Scale(zero=False)), alt.Text('Patients'), tooltip=['Patients', 'Dates', 'CGM']).properties(width=800, height=400) #.interactive()
	# c
	# pd.to_datetime(a.reducedDF['Dates'])
	# a.dfResDict['Observation']['root-effectiveDateTime']
	# ss['CGM']
	# a.reducedDF.iloc[1:10,:]
	# plt.plot(a.reducedDF['Dates'], a.reducedDF['CGM'])

	# def get_table_download_link(df):
	# 	"""Generates a link allowing the data in a given panda dataframe to be downloaded
	# 	in:  dataframe
	# 	out: href string
	# 	"""
	# 	csv = df.to_csv(index=False)
	# 	b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
	# 	# href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
	# 	href = f'<a href="data:file/csv;base64,{b64}" download="demoDataFrame.csv">Download csv file</a>'
	# 	return href

	def remove_timezone(df):
		df['Dates'] = df.apply(lambda x: x['Dates'].replace(tzinfo=None), axis=1)
		return df

	@st.cache
	def convert_df(df):
		# IMPORTANT: Cache the conversion to prevent computation on every rerun
		return df.to_csv().encode('utf-8')

	csv = convert_df(a.reducedDF[codes['CGM']]['df'])

	st.download_button(
		label="Download data as CSV",
		data=csv,
		file_name='large_df.csv',
		mime='text/csv',
	)

	# a.metadata['Patients']
	# chart_type = a.metadata['Patients'][1]
	# chart_type
	# a.getWindow(ptId=chart_type, dateStart=0, dateEnd=0)
	# a.reducedDF[codes['CGM']]['df'].apply(lambda x: x['Dates'].replace(tzinfo=None), axis=1)

	# a.reducedDF[codes['CGM']]['df'].dropna(axis='columns').info()
	# a.reducedDF[codes['CGM']]['df'].reset_index().drop([0])
	# a.reducedDF[codes['CGM']]['df'].drop([a.reducedDF[codes['CGM']]['df'].columns[i] for i in range(41)], axis=1)
	# a.reducedDF['9059-7']['df'].columns

	# display data
	with st.container():

		with st.expander("See stats"):
			if x == "mg/dL":
				st.write(a.statDict)
			else:
				st.json(a.statDict2)
		with st.expander("See raw data"):
			st.dataframe(remove_timezone(a.reducedDF[codes['CGM']]['df']))

		# st.markdown(get_table_download_link(a.reducedDF[codes['CGM']]['df']), unsafe_allow_html=True)

		# with st.expander("More stuff"):
		# 	if x == "mg/dL":
		# 		show_plot(kind="CGM time series")
		# 	else:
		# 		show_plot(kind="CGM time series 2")
		# 	show_plot(kind="aggregated")
		# if st.checkbox("See the raw data?"):
		# 	st.dataframe(a.df)
		# notes
		st.subheader("Notes")
		st.write(
			"""
			- This app uses [Streamlit](https://streamlit.io/).

			- GMI (%) = 3.31 + 0.02392 × [mean glucose in mg/dL] or GMI (mmol/mol) = 12.71 + 4.70587 × [mean glucose in mmol/L]

			- For hypoglycemic risk see Refs. \n
				(1) Kovatchev, B, et al. Algorithmic Evaluation of Metabolic Control and Risk of Severe Hypoglycemia in Type 1 and Type 2 Diabetes Using Self-Monitoring Blood Glucose Data. Diabetes Technology and Therapeutics, 5(5): 817-828, 2003.
				(2) Clarke W, Kovatchev B. Statistical Tools to Analyze Continuous Glucose Monitor Data. Diabetes Technology & Therapeutics. 2009; 11(Suppl 1): S-45-S-54. doi:10.1089/dia.2008.0138.

			Made by [JQTM](https://github.com/jquetzalcoatl).

			ADD MORE STUFF
			"""
		)

	with st.sidebar:
		st.subheader("About")
		st.write("Sin embargo, antes de llegar al verso final \
		ya había compredido que no saldría jamás de ese cuarto, pues estaba previsto \
		que la ciudad de los espejos (o los espejismos) sería arrasada por el \
		viento y desterrada de la memoria de los hombres en el instante en que \
		Aureliano Babilonia acabara de descifrar los pergaminos, y que todo lo \
		escrito en ellos era irrepetible desde siempre y para siempre porque las \
		estirpes condenadas a cien años de soledad no tenian una segunda \
		oportunidad sobre la tierra.")

if option == "Aggregated Level":
	@st.cache(allow_output_mutation=True)
	def loadData():
		return Stat(date=args.date)
	a = loadData()

	a.getWindow(ptId=0, dateStart=0, dateEnd=0)
	# st.checkbox(st.expander("Text"))
	def ptCheckbox():
		ar = {}
		row1, row2 = st.columns((2,2))
		for i,key in enumerate(a.statDF.keys()):
			if key != "units" and key != "Patients":
				if i < len(a.statDF.keys())/2:
					with row1:
						ar[key] = st.checkbox(key)
				else:
					with row2:
						ar[key] = st.checkbox(key)
		return ar


	with st.sidebar:
		options = st.multiselect(
			'Select time windows (days)',
			(7,14,21), (7))

	a.getStatsDf(ndayList = options)

	with st.sidebar:
		st.write("Select Plots:")
		ar = ptCheckbox()
		alpha = 1.0
		with st.expander("Set thresholds", expanded = True):
			thrsUL = st.slider("Select urgently low threshold", min_value=0.0, max_value = 396 * alpha, value=54 * alpha, step = alpha)
			thrsBR = st.slider("Select below range threshold", min_value=thrsUL+1 * alpha, max_value = 396 * alpha, value=thrsUL+18 * alpha, step = alpha)
			thrsAR = st.slider("Select above range threshold", min_value=thrsBR+1 * alpha, max_value = 396 * alpha, value=thrsBR+126 * alpha, step = alpha)


	a.getStatsDf(ndayList = options)
	def plotAgg():
		fig, ax = plt.subplots(figsize=(7, 7))
		s = len(a.ptAggReducedDF.keys())
		alpha=0
		for i,key in enumerate(a.ptAggReducedDF.keys()):
			ax = sns.violinplot(x='Patients', y='CGM', data=a.ptAggReducedDF[key]['df'], scale='width', inner='quartile', saturation=0.7)
			alpha = 0.4
			for violin in ax.collections[::2]:
				violin.set_alpha(alpha)
			# ax.set(title='Boxplot', xlabel='', ylabel='Height (cm)')
		st.pyplot(fig)
		# plt.show()

	def plotStats():
		fig, ax = plt.subplots(figsize=(7, 7))
		for key in ar.keys():
			if ar[key] == True:
				st.pyplot(sns.catplot(x="Patients", y=key, hue="timeWindow", kind="swarm", data=a.statDF, s=15))

	# output plots
	with st.container():
		row1, row2 = st.columns((2,2))
		with row1:
			plotAgg()
			plotStats()
		# with row2:
			# st.pyplot(sns.catplot(x="Patients", y="GMI", hue="timeWindow", kind="swarm", data=a.statDF, s=15))


	def remove_timezone(df):
		df['Dates'] = df.apply(lambda x: x['Dates'].replace(tzinfo=None), axis=1)
		return df

	@st.cache
	def convert_df(df):
		# IMPORTANT: Cache the conversion to prevent computation on every rerun
		return df.to_csv().encode('utf-8')

	csv = convert_df(a.reducedDF[codes['CGM']]['df'])

	st.download_button(
		label="Download data as CSV",
		data=csv,
		file_name='large_df.csv',
		mime='text/csv',
	)

	# display data
	with st.container():

		with st.expander("See stats"):
			pass
			# if x == "mg/dL":
			# 	st.write(a.statDict)
			# else:
			# 	st.json(a.statDict2)
		with st.expander("See raw data"):
			st.dataframe(remove_timezone(a.reducedDF[codes['CGM']]['df']))

		st.subheader("Notes")
		st.write(
			"""
			- This app uses [Streamlit](https://streamlit.io/).

			- GMI (%) = 3.31 + 0.02392 × [mean glucose in mg/dL] or GMI (mmol/mol) = 12.71 + 4.70587 × [mean glucose in mmol/L]

			- For hypoglycemic risk see Refs. \n
				(1) Kovatchev, B, et al. Algorithmic Evaluation of Metabolic Control and Risk of Severe Hypoglycemia in Type 1 and Type 2 Diabetes Using Self-Monitoring Blood Glucose Data. Diabetes Technology and Therapeutics, 5(5): 817-828, 2003.
				(2) Clarke W, Kovatchev B. Statistical Tools to Analyze Continuous Glucose Monitor Data. Diabetes Technology & Therapeutics. 2009; 11(Suppl 1): S-45-S-54. doi:10.1089/dia.2008.0138.

			Made by [JQTM](https://github.com/jquetzalcoatl).

			ADD MORE STUFF
			"""
		)

	with st.sidebar:
		st.subheader("About")
		st.write("Sin embargo, antes de llegar al verso final \
		ya había compredido que no saldría jamás de ese cuarto, pues estaba previsto \
		que la ciudad de los espejos (o los espejismos) sería arrasada por el \
		viento y desterrada de la memoria de los hombres en el instante en que \
		Aureliano Babilonia acabara de descifrar los pergaminos, y que todo lo \
		escrito en ellos era irrepetible desde siempre y para siempre porque las \
		estirpes condenadas a cien años de soledad no tenian una segunda \
		oportunidad sobre la tierra.")
