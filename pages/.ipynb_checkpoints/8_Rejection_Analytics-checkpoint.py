import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Rejection Analytics Dashboard")

# =====================================
# LOAD DATA
# =====================================

df = pd.read_excel(
    "master_production_data.xlsx",
    engine="openpyxl"
)

# =====================================
# CLEAN COLUMNS
# =====================================

df.columns = (

    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")

)

# =====================================
# REMOVE INVALID ROWS
# =====================================

df = df[
    ~df["month"].astype(str).str.contains(
        ".xlsx",
        case=False,
        na=False
    )
]

# =====================================
# NUMERIC CONVERSION
# =====================================

df["total_output"] = pd.to_numeric(
    df["total_output"],
    errors="coerce"
).fillna(0)

df["rejection"] = pd.to_numeric(
    df["rejection"],
    errors="coerce"
).fillna(0)

# =====================================
# REJECTION %
# =====================================

df["rejection_%"] = (

    df["rejection"]
    /
    df["total_output"]

) * 100

df["rejection_%"] = (
    df["rejection_%"]
    .fillna(0)
    .round(2)
)

# =====================================
# KPI SECTION
# =====================================

total_output = df[
    "total_output"
].sum()

total_rejection = df[
    "rejection"
].sum()

overall_rejection_percent = (

    total_rejection
    /
    total_output

) * 100

high_rejection_parts = len(

    df[
        df["rejection_%"] > 5
    ]

)

# =====================================
# DISPLAY KPI
# =====================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total Production",
        int(total_output)
    )

with col2:

    st.metric(
        "Total Rejection",
        int(total_rejection)
    )

with col3:

    st.metric(
        "Overall Rejection %",
        round(overall_rejection_percent, 2)
    )

with col4:

    st.metric(
        "High Rejection Parts",
        int(high_rejection_parts)
    )

# =====================================
# MONTHLY REJECTION TREND
# =====================================

st.subheader("Monthly Rejection Trend")

monthly_rejection = df.groupby(
    "month"
)[[
    "rejection",
    "total_output"
]].sum().reset_index()

monthly_rejection["rejection_%"] = (

    monthly_rejection["rejection"]
    /
    monthly_rejection["total_output"]

) * 100

fig1 = px.bar(

    monthly_rejection,

    x="month",
    y="rejection",

    title="Monthly Rejection"

)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# =====================================
# TOP REJECTION PARTS
# =====================================

st.subheader("Top Rejection Parts")

top_rejection = df.groupby(
    "part_no"
)[[
    "rejection"
]].sum().reset_index()

top_rejection = top_rejection.sort_values(
    by="rejection",
    ascending=False
)

st.dataframe(
    top_rejection.head(20)
)

# =====================================
# HIGHEST REJECTION %
# =====================================

st.subheader("Highest Rejection % Parts")

high_percent = df.sort_values(
    by="rejection_%",
    ascending=False
)

st.dataframe(

    high_percent[[
        "part_no",
        "month",
        "total_output",
        "rejection",
        "rejection_%"
    ]].head(20)

)

# =====================================
# MONTH FILTER
# =====================================

months = sorted(
    df["month"].unique()
)

selected_month = st.selectbox(
    "Select Month",
    months
)

month_df = df[
    df["month"] == selected_month
]

# =====================================
# MONTH SUMMARY
# =====================================

st.subheader(
    f"{selected_month} Rejection Analysis"
)

month_output = month_df[
    "total_output"
].sum()

month_rejection = month_df[
    "rejection"
].sum()

month_rejection_percent = (

    month_rejection
    /
    month_output

) * 100

col5, col6, col7 = st.columns(3)

with col5:

    st.metric(
        "Month Production",
        int(month_output)
    )

with col6:

    st.metric(
        "Month Rejection",
        int(month_rejection)
    )

with col7:

    st.metric(
        "Month Rejection %",
        round(month_rejection_percent, 2)
    )

# =====================================
# MONTH DATA
# =====================================

st.dataframe(month_df)

# =====================================
# REJECTION CONTRIBUTION
# =====================================

st.subheader("Rejection Contribution %")

contribution = top_rejection.head(10).copy()

contribution["contribution_%"] = (

    contribution["rejection"]
    /
    contribution["rejection"].sum()

) * 100

fig2 = px.pie(

    contribution,

    names="part_no",
    values="contribution_%",

    title="Top Rejection Contribution"

)

st.plotly_chart(
    fig2,
    use_container_width=True
)

