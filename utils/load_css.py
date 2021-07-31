"""
https://discuss.streamlit.io/t/are-you-using-html-in-markdown-tell-us-why/96/25
"""
import streamlit as st

def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

def textFunc(*args):
    return f"<div> <span class='highlight blue'> {args[0]} &emsp; </span> <br> </div> <div><span class='highlight blue'><span class='bold'>{args[1]} </span> </div>"

def statsTextFunc(args):
    return f"<div><span class='b'><span class='highlight blue'><span class='a'>Mean::&nbsp;</span><span class='bold'>{args['mean']}</span></span>&emsp;&emsp;&emsp; \
    <span class='highlight blue'><span class='a'>Min::&nbsp;</span><span class='bold'>{args['min']}</span></span>&emsp;&emsp;&emsp; \
    <span class='highlight blue'><span class='a'>Max::&nbsp;</span><span class='bold'>{args['max']}</span></span>&emsp;&emsp;&emsp; \
    <span class='highlight blue'><span class='a'>standardDev::&nbsp;</span><span class='bold'>{args['std']}</span></span>&emsp;&emsp;&emsp; \
    <span class='highlight blue'><span class='a'>Number&nbsp;of&nbsp;Days::&nbsp;</span><span class='bold'>{args['nDays']}</span></span>&emsp;&emsp;&emsp; \
    <span class='highlight blue'><span class='a'>GMI::&nbsp;</span><span class='bold'>{args['GMI']}</span></span>&emsp;&emsp;&emsp; \
    <span class='highlight blue'><span class='a'>%Urgently&nbsp;Low::&nbsp;</span><span class='bold'>{args['PerUrgentLow']}</span></span>&emsp;&emsp;&emsp; \
    <span class='highlight blue'><span class='a'>%Below&nbsp;Range::&nbsp;</span><span class='bold'>{args['PerBelowRange']}</span></span>&emsp;&emsp;&emsp; \
    <span class='highlight blue'><span class='a'>%In&nbsp;Range::&nbsp;</span><span class='bold'>{args['PerInRange']}</span></span>&emsp; &emsp; &emsp; \
    <span class='highlight blue'><span class='a'>%Above&nbsp;Range::&nbsp;</span><span class='bold'>{args['PerAboveRange']}</span></span>&emsp; &emsp; &emsp;\
    <span class='highlight blue'><span class='a'>Coeff&nbsp;Variation::&nbsp;</span><span class='bold'>{args['CoeffVariation']}</span> </span> &emsp; &emsp; &emsp; \
    <span class='highlight blue'><span class='a'>%Utilization::&nbsp;</span><span class='bold'>{args['utilizationPerc']}</span> </span> &emsp; &emsp; &emsp; \
    <span class='highlight blue'><span class='a'>Hypoglycemic&nbsp;Risk::&nbsp;</span><span class='bold'>{args['hypoRisk']}</span> </span> &emsp; &emsp; &emsp; \
    <span class='highlight blue'><span class='a'>Low&nbsp;BG&nbsp;Index::&nbsp;</span><span class='bold'>{args['LowBGIndex']}</span> </span> &emsp; &emsp; &emsp; \
    <span class='highlight blue'><span class='a'>High&nbsp;BG&nbsp;Index::&nbsp;</span><span class='bold'>{args['HighBGIndex']}</span> </span> &emsp; &emsp; &emsp; \
    </span>  </div>"
