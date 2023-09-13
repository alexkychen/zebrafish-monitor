#Predicted result comparison
import streamlit as st
import pandas as pd
import plotly.express as px
from statsmodels.tools.eval_measures import rmse

st.set_page_config(page_title="Zebrafish Activity Model Comparison", layout="wide")
st.write("""<style>
            div.block-container{padding-top:0rem;}
            div[data-testid="stMetricValue"] > div {font-size: 0.6rem;}
            </style>""", unsafe_allow_html = True)

st.title("Model performance comparison")
st.info("""The plot below shows true values of test data against predicted values (select models on the side bar).
            Each model was trained with the previous 5 days of data and make predictions on the 6th day.""", icon="🔎")

#customize plot download config
config = {
  'toImageButtonOptions': {
    'format': 'png', # one of png, svg, jpeg, webp
    'filename': 'model_comparison',
    'height': 450,
    'width': 800,
    'scale':6 # Multiply title/legend/axis/canvas sizes by this factor
  }
}

def site_info():
    st.markdown("---")
    github = "[![Github](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/alexkychen/zebrafish-monitor)"
    st.markdown(github)
    st.markdown("Developer: Alex Chen ([Contact me](mailto:alexkychen@gmail.com))")
    st.markdown("Copyright © 2023")

#Read data of test results, first column is true value
@st.cache
def read_data(filepath):
    df = pd.read_csv(filepath, index_col=0)
    df.index = pd.to_datetime(df.index)
    model_options = df.columns[1:]
    return df, model_options

#set up sidebar and options
def sidebar_param(model_options):
    with st.sidebar:
        #select results by models
        model_select = st.multiselect("Select predicted results by models", model_options)

        #select plot type (line or scatter)
        plot_type = st.selectbox("Select a plot type", ["line","scatter"])

        st.markdown("Show feeding time on main plot")
        vlines = [False, False, False]
        vlines[0] = st.checkbox("9 am")
        vlines[1] = st.checkbox("12 pm")
        vlines[2] = st.checkbox("16 pm")

        site_info()

    return model_select, vlines, plot_type

#display main plot
def main_plot(model_select, vlines, plot_type):
    choices = ["TRUE"]
    choices += model_select
    label_name = {"index":"Date/Time","value":"Mean count of every 15 minutes", "variable":"True vs. predicted"}

    #make a plot, line or scatter
    if plot_type == "line":
        fig = px.line(df, y=choices, labels=label_name)
    elif plot_type == "scatter":
        fig = px.scatter(df, y=choices, labels=label_name)

    #draw vertical line for feeding time if specified
    if vlines[0]:
        fig.add_vline(x="2021-08-16 09:00", line_color="gray")
    if vlines[1]:
        fig.add_vline(x="2021-08-16 12:00", line_color="gray")
    if vlines[2]:
        fig.add_vline(x="2021-08-16 16:00", line_color="gray")

    st.plotly_chart(fig, use_container_width=True, config=config)

def show_rmse(model_select):
    true_mean = df["TRUE"].mean()
    true_mean = round(true_mean,3)
    st.markdown(f"**True value mean**: {true_mean}")
    if len(model_select) > 0:
        st.markdown("#### Model performance measures with RMSE:")
    for model in model_select:
        error = rmse(df["TRUE"], df[model])
        error = round(error, 3)
        st.markdown(f'**{model}**: {error}')


if __name__ == "__main__":
    df, model_options = read_data("data/TestResults0816.csv")
    model_select, vlines, plot_type = sidebar_param(model_options)
    main_plot(model_select, vlines, plot_type)
    show_rmse(model_select)
