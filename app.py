import streamlit as st
import numpy as np
import pandas as pd
import time
import plotly.express as px

# Read csv from a github repo
df = pd.read_csv("https://raw.githubusercontent.com/Lexie88rus/bank-marketing-analysis/master/bank.csv")

st.set_page_config(
    page_title='Real-Time Data Science Dashboard',
    page_icon='✅',
    layout='wide'
)

# Dashboard title
st.title("Real-Time / Live Data Science Dashboard")

# Top-level filters
job_filter = st.selectbox("Select the Job", pd.unique(df['job']))

# Creating a single-element container
placeholder = st.empty()

# Dataframe filter
df_filtered = df[df['job'] == job_filter]

# Near real-time / live feed simulation
for seconds in range(200):
    df_filtered['age_new'] = df_filtered['age'] * np.random.choice(range(1, 5))
    df_filtered['balance_new'] = df_filtered['balance'] * np.random.choice(range(1, 5)))

    # Creating KPIs
    avg_age = np.mean(df_filtered['age_new'])
    count_married = int(df_filtered[df_filtered["marital"] == 'married']['marital'].count() + np.random.choice(range(1, 30)))
    balance = np.mean(df_filtered['balance_new'])

    # Display metrics for the latest values
    with placeholder.container():
        st.markdown("**Latest Metrics:**")
        st.metric(label="Age ⏳", value=round(avg_age), delta=round(avg_age) - 10)
        st.metric(label="Married Count 💍", value=int(count_married), delta=-10 + count_married)
        st.metric(label="A/C Balance ＄", value=f"$ {round(balance, 2)} ", delta=-round(balance / count_married) * 100)

        # Create two columns for charts
        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.markdown("### First Chart")
            fig = px.density_heatmap(data_frame=df_filtered, y='age_new', x='marital')
            st.plotly_chart(fig)
        with fig_col2:
            st.markdown("### Second Chart")
            fig2 = px.histogram(data_frame=df_filtered, x='age_new')
            st.plotly_chart(fig2)
        st.markdown("### Detailed Data View")
        st.dataframe(df_filtered)
        time.sleep(1)
