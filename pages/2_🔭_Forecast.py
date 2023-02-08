#Forecast into the future
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Zebrafish Activity Forecast", layout="wide")
st.write("""<style>
            div.block-container{padding-top:0rem;}
            div[data-testid="stMetricValue"] > div {font-size: 0.6rem;}
            </style>""", unsafe_allow_html = True)

st.title("Forecast future activity")
st.info("""""", icon="ℹ️")
