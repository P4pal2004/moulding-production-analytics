import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Month Comparison Dashboard",
    layout="wide"
)

st.title("Professional Production Comparison Dashboard")

# ==========================================
# LOAD DATA
# ==========================================

df = pd.read_excel(
    "master_production_data.xlsx",
    engine="openpyxl"
)

# ==========================================
# CLEAN COLUMNS
# ==========================================

df.columns = (

    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")

)

# ==========================================
# REMOVE INVALID ROWS
# ==========================================

df = df[
    ~df["month"].astype(str).str.contains(
        ".xlsx",
        case=False,
        na=False
    )
]

# ==========================================
# NUMERIC CONVERSION
# ==========================================

df["total_output"] = pd.to_numeric(
    df["total_output"],
    errors="coerce"
).fillna(0)

df["rejection"] = pd.to_numeric(
    df["rejection"],
    errors="coerce"
).fillna(0)

# ==========================================
# MONTH LIST
# ==========================================

months = sorted(
    df["month"].unique()
)

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.header("Comparison Filters")

current_month = st.sidebar.selectbox(
    "Current Month",
    months,
    index=len(months)-1
)

last_month = st.sidebar.selectbox(
    "Compare With",
    months,
    index=max(len(months)-2, 0)
)

# ==========================================
# FILTER DATA
# ==========================================

current_df = df[
    df["month"] == current_month
]

last_df = df[
    df["month"] == last_month
]

# ==========================================
# KPI CALCULATIONS
# ==========================================

current_output = current_df[
    "total_output"
].sum()

last_output = last_df[
    "total_output"
].sum()

current_rejection = current_df[
    "rejection"
].sum()

last_rejection = last_df[
    "rejection"
].sum()

current_rej_percent = (
    current_rejection
    /
    current_output
    * 100
    if current_output > 0 else 0
)

last_rej_percent = (
    last_rejection
    /
    last_output
    * 100
    if last_output > 0 else 0
)

production_change = (
    (
        current_output - last_output
    )
    /
    last_output
    * 100
    if last_output > 0 else 0
)

# ==========================================
# KPI SECTION
# ==========================================

st.subheader("Production KPI Comparison")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Current Production",
        f"{int(current_output):,}"
    )

with col2:

    st.metric(
        "Last Month Production",
        f"{int(last_output):,}"
    )

with col3:

    st.metric(
        "Production Change %",
        round(production_change, 2)
    )

with col4:

    st.metric(
        "Current Rejection %",
        round(current_rej_percent, 2)
    )

# ==========================================
# MONTH COMPARISON TABLE
# ==========================================

st.subheader("Month Comparison Summary")

comparison_df = pd.DataFrame({

    "Metric": [

        "Production",
        "Rejection",
        "Rejection %"

    ],

    current_month: [

        current_output,
        current_rejection,
        round(current_rej_percent, 2)

    ],

    last_month: [

        last_output,
        last_rejection,
        round(last_rej_percent, 2)

    ]

})

st.dataframe(
    comparison_df,
    use_container_width=True
)

# ==========================================
# PRODUCTION COMPARISON CHART
# ==========================================

st.subheader("Production Comparison")

chart_df = pd.DataFrame({

    "Month": [
        current_month,
        last_month
    ],

    "Production": [
        current_output,
        last_output
    ]

})

fig1 = px.bar(

    chart_df,

    x="Month",
    y="Production",

    text_auto=True,
    title="Production Comparison"

)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# ==========================================
# REJECTION COMPARISON
# ==========================================

st.subheader("Rejection Comparison")

rej_chart = pd.DataFrame({

    "Month": [
        current_month,
        last_month
    ],

    "Rejection": [
        current_rejection,
        last_rejection
    ]

})

fig2 = px.bar(

    rej_chart,

    x="Month",
    y="Rejection",

    text_auto=True,
    title="Rejection Comparison"

)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ==========================================
# PART-WISE COMPARISON
# ==========================================

st.subheader("Part-wise Production Comparison")

current_part = current_df.groupby(
    "part_no"
)["total_output"].sum().reset_index()

last_part = last_df.groupby(
    "part_no"
)["total_output"].sum().reset_index()

merged = pd.merge(

    current_part,
    last_part,

    on="part_no",
    how="outer",

    suffixes=(
        "_current",
        "_last"
    )

).fillna(0)

merged["difference"] = (

    merged["total_output_current"]
    -
    merged["total_output_last"]

)

merged = merged.sort_values(
    by="difference",
    ascending=False
)

st.dataframe(
    merged,
    use_container_width=True
)

# ==========================================
# TOP GAINERS
# ==========================================

st.subheader("Top Production Gainers")

gainers = merged.sort_values(
    by="difference",
    ascending=False
)

st.dataframe(
    gainers.head(10),
    use_container_width=True
)

# ==========================================
# TOP LOSERS
# ==========================================

st.subheader("Top Production Losers")

losers = merged.sort_values(
    by="difference"
)

st.dataframe(
    losers.head(10),
    use_container_width=True
)

# ==========================================
# MONTHLY TREND
# ==========================================

st.subheader("Overall Production Trend")

monthly_trend = df.groupby(
    "month"
)[[
    "total_output",
    "rejection"
]].sum().reset_index()

fig3 = go.Figure()

fig3.add_trace(

    go.Scatter(

        x=monthly_trend["month"],
        y=monthly_trend["total_output"],

        mode="lines+markers",
        name="Production"

    )

)

fig3.add_trace(

    go.Scatter(

        x=monthly_trend["month"],
        y=monthly_trend["rejection"],

        mode="lines+markers",
        name="Rejection"

    )

)

fig3.update_layout(
    title="Monthly Production & Rejection Trend"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

