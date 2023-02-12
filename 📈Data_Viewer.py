#zebrafish monitor data viewer
import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tools.eval_measures import rmse
import datetime

st.set_page_config(page_title="Zebrafish Activity Data Viewer", layout="wide")
st.write("""<style>
            div.block-container{padding-top:0rem;}
            div[data-testid="stMetricValue"] > div {font-size: 0.6rem;}
            </style>""", unsafe_allow_html = True)

st.title("Zebrafish Activity Data Viewer")
st.info("""~ Welcome to the demonstration of time series data analysis for Zebrafish Activity Monitor System.
        Please use the left side bar to select data and parameters for analysis.""", icon="🐟")

#display some info at the bottom of side bar
def site_info():
    st.markdown("---")
    github = "[![Github](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/alexkychen/zebrafish-monitor)"
    st.markdown(github)
    st.markdown("Developer: Alex Chen ([Contact me](mailto:alexkychen@gmail.com))")
    st.markdown("Copyright © 2023")

@st.cache
def read_data():
    df = pd.read_csv("data/data8.csv", index_col=0)
    df.index = pd.to_datetime(df.index)
    #calculate total count for 4 sensors
    df["Total"] = df.iloc[:].sum(axis=1).astype(int)
    first_date = df.index.min()#.strftime("%Y-%m-%d")
    last_date = df.index.max()#strftime("%Y-%m-%d")
    return df, first_date, last_date

#create sidebar
def sidebar_param(options, first_date, last_date):
    """
    options: df's column names
    first_date: first datetime index from df
    last_date: last datetime index from df
    """
    with st.sidebar:
        choices = st.multiselect("Select sensor to display", options, default="Total")

        #select date range
        start_date = st.date_input("Select start date", value=first_date, min_value=first_date, max_value=last_date)
        end_date = st.date_input("Select end date", value=first_date+timedelta(days=10), min_value=first_date, max_value=last_date)

        #select resample frequency (mean count for every X minutes)
        freq = st.number_input("Resample frequency (minute) for mean count", min_value=1, max_value=1440, value=15)

        st.markdown("Show feeding time on main plot")
        vlines = [False, False, False]
        vlines[0] = st.checkbox("9 am")
        vlines[1] = st.checkbox("12 pm")
        vlines[2] = st.checkbox("16 pm")

        site_info()

    return choices, start_date, end_date, freq, vlines

#subset data
def subset_data(df, start_date, end_date, freq):
    #convert datetime to string
    start = start_date.strftime("%Y-%m-%d")
    end = end_date.strftime("%Y-%m-%d")
    #subset data
    df = df[(df.index >= start) & (df.index <= end)]
    #resample for mean count
    period = str(freq)+"T"
    df = df.resample(period).mean()
    df.interpolate(method="linear", inplace=True)

    return df, start, end, period

#create main plot
def main_plot(df, freq, choices, vlines, start, end):
    #create Y label text
    if freq == 1:
        ylab = "Count per minute"
    else:
        ylab = "Mean count of every " + str(freq)+ " minutes"

    #create plotly plot object
    fig = px.line(df, y=choices, labels={"value":ylab, "datetime":"Date/time","variable":"Sensor"})

    #Add vertical line to indicate feeding time
    if vlines[0]:
        for i in pd.date_range(start, end):
            TL = i.strftime("%Y-%m-%d") + " 09:00"
            fig.add_vline(x=TL, line_color="gray")
    if vlines[1]:
        for i in pd.date_range(start, end):
            TL = i.strftime("%Y-%m-%d") + " 12:00"
            fig.add_vline(x=TL, line_color="gray")
    if vlines[2]:
        for i in pd.date_range(start, end):
            TL = i.strftime("%Y-%m-%d") + " 16:00"
            fig.add_vline(x=TL, line_color="gray")

    st.plotly_chart(fig, use_container_width=True)

#ETS decomposition
def ets_decomposition(df, choices, freq):
    co1, co2 = st.columns((1,4))
    co1.subheader("ETS decomposition")
    selected_data = co1.selectbox("Select sensor data", choices)
    selected_model = co1.selectbox("Select a method", ["additive", "multiplicative"])
    calculated_period = int(1440 / freq)
    co1.markdown("Period: **"+str(calculated_period)+"**")
    co1.caption("Period = 1440 / resample freq (min)")
    #co1.metric(label="Period",value=calculated_period, help="Period = 1440 / freq (min)")
    try:
        results_add = seasonal_decompose(df[selected_data], model=selected_model, period=calculated_period)
        #create ETS decomposition plot
        fig = make_subplots(rows=4, cols=1)
        fig.add_trace(go.Scatter(x=results_add.observed.index, y=results_add.observed), row=1, col=1)
        fig.add_trace(go.Scatter(x=results_add.trend.index, y=results_add.trend), row=2, col=1)
        fig.add_trace(go.Scatter(x=results_add.seasonal.index, y=results_add.seasonal), row=3, col=1)
        fig.add_trace(go.Scatter(x=results_add.resid.index, y=results_add.resid, mode='markers'), row=4, col=1)
        fig.add_hline(y=0, row=4, col=1)
        fig.update_yaxes(title_text="Observed", row=1, col=1)
        fig.update_yaxes(title_text="Trend", row=2, col=1)
        fig.update_yaxes(title_text="Seasonal", row=3, col=1)
        fig.update_yaxes(title_text="Residual", row=4, col=1)
        fig.update_layout(height=600, showlegend=False, margin=dict(t=35))
        co2.plotly_chart(fig, use_container_width=True)
        #st.plotly_chart(results_add.plot())
    except:
        co2.error("Error: Can't generate plots. Please select data or adjust parameters (e.g., Resample frequency).")
    return selected_data

#ACF and PACF
def acf_pacf(df, selected_data):
    co1, co2, co3 = st.columns((1,2,2))
    co1.subheader("ACF and PACF")
    selected_lags = co1.number_input("Enter max. lags to plot", min_value=10, max_value=250, value=100)
    co1.caption("Y-axis: Correlation coefficient")
    co1.caption("X-axis: Lag number")
    try:
        co2.pyplot(plot_acf(df[selected_data], lags=selected_lags))
    except:
        co2.error("Error: Can't generate ACF plot. Please re-select data or adjust parameters")
    try:
        co3.pyplot(plot_pacf(df[selected_data], lags=selected_lags, method="ywm"))
    except:
        co3.error("Error: Can't generate PACF plot. Please re-select data or adjust parameters")

#perform ADF stationarity test
def adf_test(df, selected_data):
    st.subheader("Augmented Dicky-Fuller Test")
    #st.markdown("Null hypothesis: time series has a unit root.")
    try:
        adftest = adfuller(df[selected_data], autolag="AIC")
    except:
        st.error("Error: Unable to perform ADF test. Please re-select data or adjust parameters.")
        st.stop()
    teststats, pvalue, lags, nobs = format(adftest[0], ".5g"), format(adftest[1], ".4g"), adftest[2], adftest[3]
    crit1, crit5, crit10 = adftest[4]["1%"], adftest[4]["5%"], adftest[4]["10%"]
    co1, co2, co3 = st.columns((1,1,2))
    co1.markdown("""
        - Test statistic: **""" + str(teststats) + """**
        - *p*-value: **""" + str(pvalue) + """**
        - Number of lags used: **""" + str(lags) + """**
        - Number of observations: **""" + str(nobs) + """**
    """)
    co2.markdown("""
        - Critical value (1%): **""" + str(format(crit1, ".5g"))+ """**
        - Critical value (5%): **""" + str(format(crit5, ".5g"))+ """**
        - Critical value (10%): **""" + str(format(crit10, ".5g"))+ """**
    """)
    #make conclusions
    co3.markdown("**Conclusion of data stationarity:**")
    if float(pvalue) > 0.05:
        co3.markdown("""*p*-value is greater than 0.05.
            We can't reject null hypothesis, and time series is considered as non-stationary.
            Applying differencing to time series is required for ARIMA based models.""")
    else:
        co3.markdown("""*p*-value is less than 0.05.
            We can reject null hypothesis, and time series is considered as stationary.
            Applying differencing to time series is not required for ARIMA based models.""")

#Predicted result comparison among models
def compare_result(filepath):
    dfr = pd.read_csv(filepath, index_col=0)
    model_options = dfr.columns[1:]
    model_select = st.multiselect("Select models", model_options)



if __name__ == "__main__":
    #read data
    df, first_date, last_date = read_data()
    #create sidebar and get some params
    choices, start_date, end_date, freq, vlines = sidebar_param(df.columns, first_date, last_date)
    #subset data
    df, start, end, period = subset_data(df, start_date, end_date, freq)

    #create main plot
    main_plot(df, freq, choices, vlines, start, end)
    #ETS decomposition
    selected_data = ets_decomposition(df, choices, freq)
    #ACF and PACF
    acf_pacf(df, selected_data)
    #ADF test
    adf_test(df, selected_data)
