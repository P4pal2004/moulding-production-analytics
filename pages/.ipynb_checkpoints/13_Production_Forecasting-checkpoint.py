import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Production Forecasting",
    layout="wide"
)

st.title("AI Production Forecasting Dashboard")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

df = pd.read_excel(
    "master_production_data.xlsx"
)

# ---------------------------------------------------
# CLEAN COLUMN NAMES
# ---------------------------------------------------

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# ---------------------------------------------------
# REQUIRED COLUMNS CHECK
# ---------------------------------------------------

required_cols = [
    "month",
    "total_output"
]

missing_cols = [
    col for col in required_cols
    if col not in df.columns
]

if missing_cols:

    st.error(
        f"Missing columns: {missing_cols}"
    )

    st.write(df.columns.tolist())

    st.stop()

# ---------------------------------------------------
# CLEAN DATA
# ---------------------------------------------------

df = df[
    ["month", "total_output"]
].copy()

df["total_output"] = pd.to_numeric(
    df["total_output"],
    errors="coerce"
)

df = df.dropna()

# ---------------------------------------------------
# GROUP MONTHLY TOTAL PRODUCTION
# ---------------------------------------------------

monthly_df = (
    df.groupby("month")["total_output"]
    .sum()
    .reset_index()
)

# ---------------------------------------------------
# CLEAN MONTH COLUMN
# ---------------------------------------------------

monthly_df["month"] = (

    monthly_df["month"]

    .astype(str)

    .str.strip()

    .str.replace("_", "-")

    .str.upper()
)

# ---------------------------------------------------
# AUTO DATE CONVERSION
# ---------------------------------------------------

monthly_df["ds"] = pd.to_datetime(

    monthly_df["month"],

    errors="coerce"
)

# ---------------------------------------------------
# REMOVE INVALID DATES
# ---------------------------------------------------

monthly_df = monthly_df.dropna(
    subset=["ds"]
)

# ---------------------------------------------------
# SORT VALUES
# ---------------------------------------------------

monthly_df = monthly_df.sort_values(
    "ds"
)

# ---------------------------------------------------
# REMOVE ZERO VALUES
# ---------------------------------------------------

monthly_df = monthly_df[
    monthly_df["total_output"] > 0
]

# ---------------------------------------------------
# SMOOTH MONTHLY PRODUCTION
# ---------------------------------------------------

monthly_df["smoothed_output"] = (

    monthly_df["total_output"]

    .rolling(
        window=3,
        min_periods=1
    )

    .mean()
)

# ---------------------------------------------------
# PROPHET FORMAT
# ---------------------------------------------------

forecast_df = monthly_df.rename(
    columns={
        "smoothed_output": "y"
    }
)

forecast_df = forecast_df[
    ["ds", "y"]
]

# ---------------------------------------------------
# SIDEBAR SETTINGS
# ---------------------------------------------------

st.sidebar.header(
    "Forecast Settings"
)

forecast_months = st.sidebar.slider(
    "Select Forecast Months",
    1,
    24,
    6
)

# ---------------------------------------------------
# TRAIN MODEL
# ---------------------------------------------------

model = Prophet(

    yearly_seasonality=True,

    weekly_seasonality=False,

    daily_seasonality=False,

    changepoint_prior_scale=0.1
)

model.fit(forecast_df)

# ---------------------------------------------------
# CREATE FUTURE DATAFRAME
# ---------------------------------------------------

future = model.make_future_dataframe(

    periods=forecast_months,

    freq="MS"
)

# ---------------------------------------------------
# FORECAST
# ---------------------------------------------------

forecast = model.predict(future)

# ---------------------------------------------------
# REMOVE NEGATIVE VALUES
# ---------------------------------------------------

forecast["yhat"] = forecast[
    "yhat"
].clip(lower=0)

forecast["yhat_lower"] = forecast[
    "yhat_lower"
].clip(lower=0)

forecast["yhat_upper"] = forecast[
    "yhat_upper"
].clip(lower=0)

# ---------------------------------------------------
# REMOVE HISTORICAL MONTHS
# ---------------------------------------------------

last_actual_date = forecast_df["ds"].max()

future_only = forecast[
    forecast["ds"] > last_actual_date
].copy()

# ---------------------------------------------------
# RESET INDEX
# ---------------------------------------------------

future_only = future_only.reset_index(
    drop=True
)

# ---------------------------------------------------
# KPI VALUES
# ---------------------------------------------------

latest_actual = int(
    monthly_df["total_output"].iloc[-1]
)

forecast_value = int(
    future_only["yhat"].iloc[0]
)

growth_percent = round(

    (
        (
            forecast_value
            -
            latest_actual
        )
        /
        latest_actual
    ) * 100,

    2
)

# ---------------------------------------------------
# MONTH DISPLAY
# ---------------------------------------------------

latest_month = (
    forecast_df["ds"]
    .max()
    .strftime("%b-%Y")
)

forecast_month = (
    future_only["ds"]
    .iloc[0]
    .strftime("%b-%Y")
)

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(

        f"Latest Production ({latest_month})",

        f"{latest_actual:,}"
    )

with col2:

    st.metric(

        f"Forecast Production ({forecast_month})",

        f"{forecast_value:,}"
    )

with col3:

    st.metric(

        "Expected Growth %",

        f"{growth_percent}%"
    )

# ---------------------------------------------------
# FORECAST CHART
# ---------------------------------------------------

st.subheader(
    "Monthly Production Forecast"
)

fig = px.line(

    forecast,

    x="ds",

    y="yhat",

    title="AI Production Forecast Trend"
)

# ACTUAL DATA

fig.add_scatter(

    x=forecast_df["ds"],

    y=forecast_df["y"],

    mode="lines+markers",

    name="Actual Production"
)

# LOWER FORECAST

fig.add_scatter(

    x=forecast["ds"],

    y=forecast["yhat_lower"],

    mode="lines",

    name="Lower Forecast",

    line=dict(dash="dot")
)

# UPPER FORECAST

fig.add_scatter(

    x=forecast["ds"],

    y=forecast["yhat_upper"],

    mode="lines",

    name="Upper Forecast",

    line=dict(dash="dot")
)

fig.update_layout(

    xaxis_title="Month",

    yaxis_title="Production",

    height=600
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------------------------
# FORECAST TABLE
# ---------------------------------------------------

st.subheader(
    "Future Forecast Data"
)

forecast_table = future_only[
    [
        "ds",
        "yhat",
        "yhat_lower",
        "yhat_upper"
    ]
].copy()

forecast_table.columns = [

    "Forecast Month",

    "Predicted Production",

    "Lower Estimate",

    "Upper Estimate"
]

forecast_table[
    "Forecast Month"
] = forecast_table[
    "Forecast Month"
].dt.strftime("%b-%Y")

forecast_table[
    "Predicted Production"
] = forecast_table[
    "Predicted Production"
].astype(int)

forecast_table[
    "Lower Estimate"
] = forecast_table[
    "Lower Estimate"
].astype(int)

forecast_table[
    "Upper Estimate"
] = forecast_table[
    "Upper Estimate"
].astype(int)

st.dataframe(
    forecast_table,
    use_container_width=True
)

# ---------------------------------------------------
# HISTORICAL TREND
# ---------------------------------------------------

st.subheader(
    "Historical Production Trend"
)

hist_fig = px.area(

    monthly_df,

    x="ds",

    y="total_output",

    title="Historical Monthly Production"
)

st.plotly_chart(
    hist_fig,
    use_container_width=True
)

# ---------------------------------------------------
# FORECAST INSIGHTS
# ---------------------------------------------------

st.subheader(
    "AI Forecast Insights"
)

if growth_percent > 0:

    st.success(

        f"""
        Production is expected to increase by
        {growth_percent}% in {forecast_month}.
        """
    )

else:

    st.warning(

        f"""
        Production may decrease by
        {abs(growth_percent)}% in {forecast_month}.
        """
    )

# ---------------------------------------------------
# DOWNLOAD REPORT
# ---------------------------------------------------

csv = forecast_table.to_csv(
    index=False
)

st.download_button(

    label="Download Forecast Report",

    data=csv,

    file_name="production_forecast.csv",

    mime="text/csv"
)

