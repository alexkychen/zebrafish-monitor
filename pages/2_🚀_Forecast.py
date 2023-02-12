#Forecast and anomaly detection by adjust significant levels
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import time
from datetime import timedelta
from scipy.stats import norm

st.set_page_config(page_title="Zebrafish Activity Forecast and Anomaly Detection", layout="wide")
st.write("""<style>
            div.block-container{padding-top:0rem;}
            div[data-testid="stMetricValue"] > div {font-size: 0.6rem;}
            </style>""", unsafe_allow_html = True)

st.title("Forecast and detect behavioral anomalies")
st.info("""Please select a forecasting model and significance level on the left
        side bar to see the the animation of forecasting zebrafish activity on
        the day of August 16th. A gray area of confidence intervals will be drawn
        based on your significance level. After the animation, the lower bound of
        confidence intervals is used to detect outliers, if any.
        """, icon="🔎")

#display some info at the bottom of side bar
def site_info():
    st.markdown("---")
    github = "[![Github](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/alexkychen/zebrafish-monitor)"
    st.markdown(github)
    st.markdown("Developer: Alex Chen ([Contact me](mailto:alexkychen@gmail.com))")
    st.markdown("Copyright © 2023")

@st.cache(allow_output_mutation=True)
def read_data():
    df = pd.read_csv("data/forecast2.csv", index_col=0)
    df.index = pd.to_datetime(df.index)
    return df

def sidebar_param():
    with st.sidebar:
        with st.form("sidebar"):
            model = st.selectbox("Select a forecasting model", ["SARIMA","SARIMAX","Prophet","XGBoost"])
            alpha = st.number_input("Significance level (alpha)", max_value=1.0, min_value=0.01, value=0.05)
            if st.form_submit_button("Submit"):
                st.experimental_rerun()
        site_info()
    return model, alpha

def computer_ci(data, alpha):
    """
    data: Pandas Series or array-like
    """
    n_samples = len(data)
    z = norm.ppf(1-alpha/2)
    std = data.std(ddof=n_samples - 1)
    se = std / np.sqrt(n_samples)
    #print(f"SE: {se}")
    upper = data + (z * se)
    lower = data - (z * se)
    return upper, lower


def draw_plot(df, model, alpha):
    #set up a new df copy for plotting
    dfcopy = pd.DataFrame(index = df.index,
                          columns = ["Training","True value",model,"upper","lower"])
    dfcopy = dfcopy.applymap(lambda x: np.nan)
    dfcopy["Training"] = df["Training"]

    #set up start and end point for plot's x-axis
    start = df.index.min()
    end = df.index.max()

    #compute CI
    predicted_data = df[model][-96:]
    upper, lower = computer_ci(predicted_data, alpha)
    upper = upper.apply(lambda x: 0 if x < 0 else x)
    lower = lower.apply(lambda x: 0 if x < 0 else x)
    df["upper"] = upper
    df["lower"] = lower
    #% CI for legend label
    perct_ci = str(int((1 - alpha)*100))

    #start the plot
    fig = px.line(dfcopy["Training"])
    #set up a page container for plotting
    container = st.empty()
    container.plotly_chart(fig, use_container_width=True)

    #get column index by model name
    col_idx = df.columns.get_loc(model)

    #set a new name for legend
    dfcopy.rename(columns = {model:"Predicted by "+model}, inplace=True)

    for i in range(96):
        #add new row to dfcopy
        dfcopy.iloc[385+i,0:5] = df.iloc[385+i, [0,1,col_idx,6,7]]
        #draw training data and predicted values
        fig = px.line(dfcopy.iloc[:,[0,2]],
                      color_discrete_sequence = ["royalblue","red"],
                      labels = {"value":"Mean count","index":"Date/time","variable":""})
        #draw upper bound
        fig.add_trace(go.Scatter(
            x = dfcopy.index[0:385+i],
            y = dfcopy.upper[0:385+i],
            mode = "lines",
            line_color = "lightgray",
            name = perct_ci+"% CI"
        ))
        #draw lower bound
        fig.add_trace(go.Scatter(
            x = dfcopy.index[0:385+i],
            y = dfcopy.lower[0:385+i],
            mode = "lines",
            line_color = "lightgray",
            fill='tonexty',
            name = perct_ci+"% CI"
        ))
        #draw true values
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

    forecast_df = dfcopy.iloc[-96:, -4:]
    #st.dataframe(forecast_df)
    return forecast_df

def detect_outlier(forecast_df):
    co1, co2 = st.columns(2)
    if any(forecast_df["True value"] < forecast_df["lower"]):
        display_df = forecast_df[forecast_df["True value"] < forecast_df["lower"]][["True value","lower"]]
        display_df.rename(columns = {"lower":"Lower bound"}, inplace=True)
        #reformat datetime index
        display_df.index = display_df.index.strftime("%Y-%m-%d %H:%M %p")
        co1.warning("Outliers were detected. Fish activity might be lower than predicted range.", icon="⚠️")
        co2.markdown("Low activity was found at the following time.")
        co2.dataframe(display_df)
    else:
        co1.info("No outlier was found.", icon="👌")


if __name__ == "__main__":
    df = read_data()
    model, alpha = sidebar_param()
    forecast_df = draw_plot(df, model, alpha)
    detect_outlier(forecast_df)
