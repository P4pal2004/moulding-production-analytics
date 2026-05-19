import streamlit as st
import pandas as pd

st.title("Production Summary Dashboard")

# LOAD DATA
df = pd.read_excel(
    "master_production_data.xlsx"
)

# CLEAN COLUMNS
df.columns = df.columns.str.strip()

# REMOVE INVALID MONTH ROWS
df = df[
    ~df["Month"].astype(str).str.contains(
        ".xlsx",
        case=False,
        na=False
    )
]


# KPI SECTION
total_production = df["Total Output"].sum()
total_rejection = df["Rejection"].sum()

rejection_percent = (
    total_rejection / total_production * 100
)

total_parts = df["Part No"].nunique()

# DISPLAY KPIs
col1, col2, col3, col4 = st.columns(4)

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

with col3:
    st.metric(
        "Rejection %",
        round(rejection_percent, 2)
    )

with col4:
    st.metric(
        "Unique Parts",
        total_parts
    )

# MONTH FILTER
months = sorted(df["Month"].unique())

selected_month = st.selectbox(
    "Select Month",
    months
)

filtered_df = df[
    df["Month"] == selected_month
]

# MONTH SUMMARY
st.subheader("Selected Month Data")

st.dataframe(filtered_df)

# TOP PRODUCTION PARTS
st.subheader("Top Production Parts")

top_parts = filtered_df.groupby(
    "Part No"
)[["Total Output"]].sum().reset_index()

top_parts = top_parts.sort_values(
    by="Total Output",
    ascending=False
)

st.dataframe(top_parts.head(10))

# TOP REJECTION PARTS
st.subheader("Top Rejection Parts")

top_rejection = filtered_df.groupby(
    "Part No"
)[["Rejection"]].sum().reset_index()

top_rejection = top_rejection.sort_values(
    by="Rejection",
    ascending=False
)

st.dataframe(top_rejection.head(10))

# MONTHLY SUMMARY
st.subheader("Monthly Summary")

monthly_summary = df.groupby(
    "Month"
)[["Total Output", "Rejection"]].sum().reset_index()

st.dataframe(monthly_summary)

