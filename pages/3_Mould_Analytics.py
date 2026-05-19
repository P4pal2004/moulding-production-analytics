import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Mould Analytics",
    layout="wide"
)

st.title("Mould Analytics Dashboard")

# ---------------------------------------------------
# READ EXCEL
# ---------------------------------------------------

master_df = pd.read_excel(
    "MASTER DATA OF MOULDING.xlsx",
    header=2
)

# ---------------------------------------------------
# FILL MERGED CELLS
# ---------------------------------------------------

master_df['MATERIAL RATE KG'] = (
    master_df['MATERIAL RATE KG']
    .ffill()
)

# ---------------------------------------------------
# NUMERIC CONVERSION
# ---------------------------------------------------

master_df['SCHEDULE'] = pd.to_numeric(
    master_df['SCHEDULE'],
    errors='coerce'
)

master_df['shift output moulding'] = pd.to_numeric(
    master_df['shift output moulding'],
    errors='coerce'
)

master_df['Charge Weight (Grams)'] = pd.to_numeric(
    master_df['Charge Weight (Grams)'],
    errors='coerce'
)

# ---------------------------------------------------
# RM REQUIRED
# ---------------------------------------------------

master_df['RM Required KG'] = (
    master_df['SCHEDULE'] *
    master_df['Charge Weight (Grams)']
) / 1000

# ---------------------------------------------------
# REQUIRED SHIFTS
# ---------------------------------------------------

master_df['Required Shifts'] = (
    master_df['SCHEDULE'] /
    master_df['shift output moulding']
)

# ---------------------------------------------------
# MOULD SUMMARY
# ---------------------------------------------------

mould_summary = (
    master_df
    .groupby(
        [
            'Mould No',
            'machine tonnage'
        ],
        as_index=False
    )
    .agg({
        'SCHEDULE': 'sum',
        'RM Required KG': 'sum',
        'Required Shifts': 'sum'
    })
)

# ---------------------------------------------------
# AVAILABLE SHIFTS
# ---------------------------------------------------

mould_summary['Available Shifts'] = (
    mould_summary['machine tonnage']
    .map({
        '100T': 312,
        '150T': 260
    })
)

# ---------------------------------------------------
# UTILISATION %
# ---------------------------------------------------

mould_summary['Utilisation %'] = (
    mould_summary['Required Shifts'] /
    mould_summary['Available Shifts']
) * 100

# ---------------------------------------------------
# STATUS
# ---------------------------------------------------

mould_summary['Status'] = (
    mould_summary['Utilisation %']
    .apply(
        lambda x:
        'Underloaded' if x < 70
        else 'Normal' if x <= 100
        else 'Overloaded'
    )
)

# ---------------------------------------------------
# SHOW TABLE
# ---------------------------------------------------

st.subheader("Mould-wise Summary")

st.dataframe(mould_summary)

# ---------------------------------------------------
# CHART
# ---------------------------------------------------

fig = px.bar(
    mould_summary,
    x='Mould No',
    y='Utilisation %',
    color='machine tonnage',
    title='Mould Utilisation'
)

st.plotly_chart(fig)