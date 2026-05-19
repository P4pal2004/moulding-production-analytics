import streamlit as st
import pandas as pd

st.title("Historical Production Analytics")

# LOAD MASTER DATA
df = pd.read_excel(
    "master_production_data.xlsx"
)

# CLEAN COLUMN NAMES
df.columns = df.columns.str.strip()
# REMOVE INVALID MONTH ROWS
df = df[
    ~df["Month"].astype(str).str.contains(
        ".xlsx",
        case=False,
        na=False
    )
]


# SHOW DATA
st.subheader("Historical Production Data")

st.dataframe(df)

# KPIs
total_production = df["Total Output"].sum()
total_rejection = df["Rejection"].sum()

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Total Production",
        int(total_production)
    )

with col2:
    st.metric(
        "Total Rejection",
        int(total_rejection)
    )

# MONTHLY SUMMARY
st.subheader("Monthly Production Summary")

monthly_summary = df.groupby(
    "Month"
)[["Total Output", "Rejection"]].sum().reset_index()

st.dataframe(monthly_summary)

# PART WISE SUMMARY
st.subheader("Top Production Parts")

top_parts = df.groupby(
    "Part No"
)[["Total Output"]].sum().reset_index()

top_parts = top_parts.sort_values(
    by="Total Output",
    ascending=False
)

st.dataframe(top_parts.head(20))

