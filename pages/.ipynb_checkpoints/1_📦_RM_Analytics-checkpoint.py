import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="RM Analytics",
    layout="wide"
)

st.title("Raw Material Analytics")

# Read Excel
master_df = pd.read_excel(
    "MASTER DATA OF MOULDING.xlsx",
    header=2
)

# Fill merged cells
master_df['MATERIAL RATE KG'] = (
    master_df['MATERIAL RATE KG']
    .ffill()
)

# Numeric conversion
master_df['Charge Weight (Grams)'] = pd.to_numeric(
    master_df['Charge Weight (Grams)'],
    errors='coerce'
)

master_df['SCHEDULE'] = pd.to_numeric(
    master_df['SCHEDULE'],
    errors='coerce'
)

# RM Required
master_df['RM Required KG'] = (
    master_df['SCHEDULE'] *
    master_df['Charge Weight (Grams)']
) / 1000

# RM Summary
rm_summary = (
    master_df
    .groupby(
        'Raw Material Grade',
        as_index=False
    )
    .agg({
        'RM Required KG': 'sum'
    })
)

# Chart
fig = px.bar(
    rm_summary,
    x='Raw Material Grade',
    y='RM Required KG',
    title='Raw Material Consumption'
)

st.plotly_chart(fig)

# Table
st.dataframe(rm_summary)