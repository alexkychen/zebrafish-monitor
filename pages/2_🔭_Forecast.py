#Forecast into the future
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import time
from datetime import timedelta

st.set_page_config(page_title="Zebrafish Activity Forecast", layout="wide")
st.write("""<style>
            div.block-container{padding-top:0rem;}
            div[data-testid="stMetricValue"] > div {font-size: 0.6rem;}
            </style>""", unsafe_allow_html = True)

st.title("Forecast future activity")
st.info("""Please select a forecasting model on the left side bar to see the
        animation of forecasting zebrafish activity on the day of August 16th.
        A gray area of confidence intervals will be included in the plot and
        it can be used to detect outliers.""", icon="ℹ️")

#display some info at the bottom of side bar
def site_info():
    st.markdown("---")
    github = "[![Github](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/alexkychen/zebrafish-monitor)"
    st.markdown(github)
    st.markdown("Developer: Alex Chen ([Contact me](mailto:alexkychen@gmail.com))")
    st.markdown("Copyright © 2023")

@st.cache
def read_data():
    df = pd.read_csv("data/forecast.csv", index_col=0)
    df.index = pd.to_datetime(df.index)
    df = df.applymap(lambda x: 0 if x < 0 else x)
    return df

def sidebar_param():
    with st.sidebar:
        model = st.selectbox("Select a forecasting model", ["SARIMA","SARIMAX","Prophet","XGBoost"])
        site_info()
    return model

def draw_plot(df, model):
    #set up a df copy
    dfcopy = df.copy()
    dfsize = len(dfcopy)
    dfcopy.iloc[-96:] = np.nan
    fig = px.line(dfcopy["Training"])

    #set up a page container for plotting
    container = st.empty()
    container.plotly_chart(fig, use_container_width=True)

    #dictionary to store paired variables
    #model name as key, column name as values
    var_dict = {"SARIMA": ["Predicted_SARIMA","SARIMA_upper","SARIMA_lower"],
                "SARIMAX": ["Predicted_SARIMAX","SARIMAX_upper","SARIMAX_lower"],
                "Prophet": ["Predicted_Prophet","Prophet_upper","Prophet_lower"],
                "XGBoost": ["Predicted_XGBoost","XGBoost_upper","XGBoost_lower"]}

    #set up start and end point for plot's x-axis
    start = df.index.min()
    end = df.index.max()

    for i in range(96):

        dfcopy.iloc[385+i,] = df.iloc[385+i,]
        fig = px.line(dfcopy[["Training",var_dict[model][0]]],
                      color_discrete_sequence=["royalblue","red"],
                      labels={"value":"Mean count", "index":"Date/time","variable":""})
        fig.add_trace(go.Scatter(
            x = dfcopy.index[0:385+i],
            y = dfcopy[var_dict[model][1]][0:385+i],
            mode = "lines",
            line_color = "lightgray",
            name = "Confidence Interval"
        ))
        fig.add_trace(go.Scatter(
            x = dfcopy.index[0:385+i],
            y = dfcopy[var_dict[model][2]][0:385+i],
            mode = "lines",
            line_color = "lightgray",
            fill='tonexty',
            name = "Confidence Interval"
        ))
        fig.add_trace(go.Scatter(
            x = dfcopy.index[0:385+i],
            y = dfcopy.iloc[0:385+i,1],
            mode = "markers",
            line_color = "gray",
            name = "True values"
        ))
        fig.update_xaxes(range=(start, end + timedelta(hours=2)))
        container.plotly_chart(fig, use_container_width=True)
        time.sleep(0.003)

def detect_outlier(df, model):
    if model == "SARIMA":
        if any(df["True"] < df["SARIMA_lower"]):
            st.text("Outliers are detected.")
        else:
            st.text("No outlier was found.")


if __name__ == "__main__":
    df = read_data()
    model = sidebar_param()
    draw_plot(df, model)
    #detect_outlier(df, model)

#
# dfcopy = df.copy()
# dfsize = len(dfcopy)
# dfcopy["pred"] = np.nan
# dfcopy.iloc[300:] = np.nan
# fig = px.line(dfcopy["Total"])
#
# container = st.empty()
# container.plotly_chart(fig, use_container_width=True)
#
# for i in range(dfsize-300):
#     dfcopy.iloc[i+300,5]= df.iloc[i+300,4]
#     fig = px.line(dfcopy[["Total","pred"]])
#     container.plotly_chart(fig, use_container_width=True)
#     time.sleep(0.005)



# mydf = df.iloc[0:100]
# fig = px.line(mydf["Total"])
#
# #co1, co2 = st.columns(2)
# container = st.empty()
# container.plotly_chart(fig, use_container_width=True)
#
# #for t in pd.date_range(start, end, freq="15T"):
# for i in range(200):
#     mydf = df.iloc[0:100+i]
#     fig = px.line(mydf["Total"])
#     container.plotly_chart(fig, use_container_width=True)
#     time.sleep(0.01)
