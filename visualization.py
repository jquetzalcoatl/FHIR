import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from datetime import datetime, date
import seaborn as sns
import altair as alt
from utils.stats import stats
import argparse
import os

####
# os.getcwd()
# os.chdir(os.path.join(os.getcwd(), "FHIR"))

# $streamlit run visualization.py -- --date 2021-07-06
# https://github.com/streamlit/streamlit/issues/337#issuecomment-544860528

#PARSING
parser = argparse.ArgumentParser(description='This app shows CGM')

parser.add_argument('--date', dest="date", type=str, default="2021-07-05",
					help='Specify date since tag for FHIR bulk export. \n Default set to 2021-07-05')

try:
    args = parser.parse_args()
except SystemExit as e:
    # This exception will be raised if --help or invalid command line arguments
    # are used. Currently streamlit prevents the program from exiting normally
    # so we have to do a hard exit.
    os._exit(e.code)

# a = stats(date="2021-06-15", MAX=5)

path = os.getcwd() + "/TS-BulkExport-" + args.date
# path = os.getcwd() + "/TS-BulkExport-" + "2021-07-05"

#LOADING
import json
def loadJSON(filename = path + "/Observations.json"):
	with open(filename, 'r') as h:
		js = json.load(h)
	return js

jsonObj = loadJSON()

df = pd.read_csv(path + "/Observations.csv")

a = stats((jsonObj, df))
# a.df
###
# a.Obs[0]
#Dashboard
# can only set this once, first thing to set
apptitle = 'TS-Registry Dashboard'
st.set_page_config(page_title=apptitle, layout="wide")

with st.beta_container():
	st.title("TS Data Visualization Demo")
	st.header(f'Showing dummy data! from bulk export ({args.date})')
	# st.write("""See the code and plots for five libraries at once.""")

# LAYING OUT THE TOP SECTION OF THE APP
# row1_1, row1_2 = st.beta_columns((2,2))
# np.max(a.dates)
# with row1_1:
# 	st.title("Patient")
# 	chart_type = st.selectbox("Choose Patient", np.unique(a.Pts).tolist())

with st.sidebar:
	with st.beta_expander("Choose Patient"):
		chart_type = st.selectbox("", np.unique(a.Pts).tolist())

a.getWindow(ptId=chart_type, dateStart=0, dateEnd=0)

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
with st.beta_container():
	st.title("Time Window")
	hour_selected0 = (a.getDate(str(a.reducedDF['Dates'].iloc[0])), a.getDate(str(a.reducedDF['Dates'].iloc[-1])))
	hour_selected = st.slider("Select Time Window", key='timeSlider', value=hour_selected0, min_value=hour_selected0[0], max_value=hour_selected0[1])

# row1_1, row1_2 = st.beta_columns((2,2))
# with row1_1:
# 	hour_s0 = st.date_input("Start date", value = hour_selected[0], key='calendar1', min_value=hour_selected0[0], max_value=hour_selected0[1], on_change=update_timeSliderLeft)
#
# with row1_2:
# 	hour_s1 = st.date_input("End date", value = hour_selected[1], key='calendar2', min_value=hour_selected0[0], max_value=hour_selected0[1], on_change=update_timeSliderRight)

a.getWindow2(ptId=chart_type, dateStart=hour_selected[0], dateEnd=hour_selected[1])
thrsUL=55
thrsBR=80
thrsAR=200
# a.getStats(thrsUL=55, thrsBR=80, thrsAR=200)

with st.sidebar:
	# show_params = st.checkbox("Set thresholds", False)
	# if show_params:
	with st.beta_expander("Set thresholds"):
		thrsUL = st.slider("Select urgently low threshold", min_value=0, max_value = 400, value=55)
		thrsBR = st.slider("Select below range threshold", min_value=thrsUL+1, max_value = 400, value=thrsUL+25)
		thrsAR = st.slider("Select above range threshold", min_value=thrsBR+1, max_value = 400, value=thrsBR+120)

with st.beta_container():
	# show_params = st.checkbox("Set thresholds", False)
	# if show_params:
	# 	thrsUL = st.slider("Select urgently low threshold", min_value=0, max_value = 400, value=55)
	# 	thrsBR = st.slider("Select below range threshold", min_value=thrsUL+1, max_value = 400, value=thrsUL+25)
	# 	thrsAR = st.slider("Select above range threshold", min_value=thrsBR+1, max_value = 400, value=thrsBR+120)
	st.subheader(f"Displaying:  {chart_type}")
	st.write("")

a.getStats(thrsUL=thrsUL, thrsBR=thrsBR, thrsAR=thrsAR)

# sns.lineplot(data=a.reducedDF.iloc[:,1:2], palette=['blue'], linewidth=2.5, hue="red", style="red", c='red')
def coloring(x, thrsUL=55, thrsBR=80, thrsAR=200):
	if x < thrsUL:
		return 'red'
	elif x < thrsBR:
		return 'orange'
	elif x < thrsAR:
		return 'green'
	else:
		return 'red'

# sns.histplot(a.reducedDF['CGM'], kde=True, color='red', bins=10)
# create plots
def show_plot(kind: str):
	st.write(kind)
	if kind == "CGM time series":
		fig, ax = plt.subplots()
		ax.set_xticklabels(a.dates, rotation=45)
		ax.set_xlabel("Date")
		ax.set_ylabel("CGM (mg/dL)")
		ll = a.reducedDF.shape[0]
		ax.plot([a.getDate(str(a.reducedDF.iloc[i,2])) for i in range(a.reducedDF.shape[0])], a.reducedDF.iloc[:,1], c='black', linewidth=0.05)#matplotlib_plot(chart_type, df)
		ax.scatter([a.getDate(str(a.reducedDF.iloc[i,2])) for i in range(a.reducedDF.shape[0])], a.reducedDF.iloc[:,1], c=[coloring(a.reducedDF.iloc[i,1], thrsUL=thrsUL, thrsBR=thrsBR, thrsAR=thrsAR) for i in range(a.reducedDF.shape[0])])
		st.pyplot(fig)
	elif kind == "CGM Histogram":
		fig, ax = plt.subplots()
		ax.set_xticklabels(a.CGM, rotation=0)
		# ax.hist(a.reducedDF['CGM'], normed=1)#matplotlib_plot(chart_type, df)
		b = st.slider("Select number of bins", min_value=1, max_value = 100, value=10)
		sns.histplot(a.reducedDF['CGM'], ax=ax, kde=True, bins=b)
		# sns.displot(a.reducedDF['CGM'], ax=ax)
		st.pyplot(fig)
	elif kind == "Matplotlib":
		fig = Figure()
		ax = fig.subplots()
		ax.set_xticklabels(a.dates, rotation=45)
		ax.set_xlabel("Date")
		ax.set_ylabel("CGM")
		sns.lineplot(data=a.reducedDF.iloc[:,1:2], ax=ax, hue="event", style="event", c='red')
		# st.plotly_chart(plot, use_container_width=True)
		st.pyplot(fig)
	elif kind == "altair":
		# df = pd.DataFrame(np.random.randn(200, 3),columns=['a', 'b', 'c'])
		c = alt.Chart(a.reducedDF).mark_line(point=True).encode(alt.X('Dates', axis=alt.Axis(labelAngle=-45), scale=alt.Scale(zero=False)), alt.Y('CGM', scale=alt.Scale(zero=False)), tooltip=['Patients', 'Dates', 'CGM']).properties(width=800, height=400).interactive()
		linethrsUL = alt.Chart(pd.DataFrame({'CGM': [thrsUL]})).mark_rule().encode(y='CGM')
		linethrsBR = alt.Chart(pd.DataFrame({'CGM': [thrsBR]})).mark_rule().encode(y='CGM')
		linethrsAR = alt.Chart(pd.DataFrame({'CGM': [thrsAR]})).mark_rule().encode(y='CGM')
		st.write(c + linethrsUL + linethrsBR + linethrsAR)
		# x='Dates'


# output plots
with st.beta_container():
	show_plot(kind="altair")

two_cols = True#st.checkbox("2 columns?", True)
if two_cols:
	col1, col2 = st.beta_columns(2)

col1, col2 = st.beta_columns(2)

if two_cols:
	with col1:
		show_plot(kind="CGM time series")
	with col2:
		show_plot(kind="CGM Histogram")
	# with col1:
	# 	show_plot(kind="altair")
	# with col2:
	# 	show_plot(kind="Matplotlib")
	# with col1:
	# 	show_plot(kind="Matplotlib")
	# with col2:
	# 	show_plot(kind="Matplotlib")
else:
	with st.beta_container():
		for lib in libs:
			show_plot(kind=lib)

# display data
with st.beta_container():
	# show_plot(kind="altair")
	# show_plot(kind="CGM time series")
	# show_stats = st.checkbox("See stats", True)
	# if st.checkbox("See stats", True):
	# 	st.json(a.statDict)
	with st.beta_expander("See Stats"):
		st.json(a.statDict)
	# show_data = st.checkbox("See the raw data?")
	with st.beta_expander("See raw data"):
		st.dataframe(a.df)
	# if st.checkbox("See the raw data?"):
	# 	st.dataframe(a.df)
	# notes
	st.subheader("Notes")
	st.write(
		"""
		- This app uses [Streamlit](https://streamlit.io/).

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
