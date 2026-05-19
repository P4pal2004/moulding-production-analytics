import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Power Consumption Analytics",
    layout="wide"
)

st.title("Power Consumption & Energy Analytics")

# =========================================
# LOAD DATA
# =========================================

df = pd.read_excel(
    "MASTER DATA OF MOULDING.xlsx",
    header=2,
    engine="openpyxl"
)

# =========================================
# CLEAN COLUMNS
# =========================================

df.columns = (

    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("(", "")
    .str.replace(")", "")

)

# =========================================
# FIX MERGED CELLS
# =========================================

df = df.ffill()

# =========================================
# REQUIRED COLUMNS
# =========================================

required_cols = [

    "part_no",
    "motor_hp",
    "heater_watt",
    "schedule",
    "shift_output_moulding",
    "machine_tonnage"

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

# =========================================
# NUMERIC CONVERSION
# =========================================

numeric_cols = [

    "motor_hp",
    "heater_watt",
    "schedule",
    "shift_output_moulding"

]

for col in numeric_cols:

    df[col] = (

        df[col]
        .astype(str)
        .str.replace(",", "")
        .str.strip()

    )

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)

# =========================================
# REMOVE INVALID ROWS
# =========================================

df = df[
    df["schedule"] > 0
]

# =========================================
# REMOVE DUPLICATE PARTS
# =========================================

df["part_no"] = (

    df["part_no"]
    .astype(str)
    .str.strip()

)

df = df.drop_duplicates(
    subset="part_no"
)

# =========================================
# REQUIRED SHIFTS
# =========================================

df["required_shifts"] = (

    df["schedule"]
    /
    df["shift_output_moulding"]

)

df["required_shifts"] = (
    df["required_shifts"]
    .fillna(0)
)

# =========================================
# RUNTIME HOURS
# =========================================

df["runtime_hours"] = (

    df["required_shifts"]
    *
    12

)

# =========================================
# MOTOR POWER
# =========================================

df["motor_kw"] = (

    df["motor_hp"]
    *
    0.746

)

# =========================================
# HEATER POWER
# =========================================

df["heater_kw"] = (

    df["heater_watt"]
    /
    1000

)

# =========================================
# ACTUAL RUNNING LOAD
# =========================================

MOTOR_LOAD_FACTOR = 0.7
HEATER_LOAD_FACTOR = 0.5

df["actual_power_kw"] = (

    (df["motor_kw"] * MOTOR_LOAD_FACTOR)
    +
    (df["heater_kw"] * HEATER_LOAD_FACTOR)

)

# =========================================
# POWER CONSUMPTION
# =========================================

df["power_consumption_kwh"] = (

    df["actual_power_kw"]
    *
    df["runtime_hours"]

)

# =========================================
# ELECTRICITY RATE
# =========================================

electricity_rate = st.sidebar.number_input(

    "Electricity Rate ₹/Unit",

    min_value=1.0,
    value=10.0

)

# =========================================
# ELECTRICITY COST
# =========================================

df["electricity_cost"] = (

    df["power_consumption_kwh"]
    *
    electricity_rate

)

# =========================================
# POWER COST PER PART
# =========================================

df["power_cost_per_part"] = (

    df["electricity_cost"]
    /
    df["schedule"]

)

# =========================================
# KPI SECTION
# =========================================

total_power = df[
    "power_consumption_kwh"
].sum()

total_cost = df[
    "electricity_cost"
].sum()

avg_cost_per_part = df[
    "power_cost_per_part"
].mean()

avg_power_per_part = (

    total_power
    /
    df["schedule"].sum()

)

# =========================================
# KPI DISPLAY
# =========================================

st.subheader("Power Consumption KPI")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total Power Consumption",
        f"{round(total_power, 2)} kWh"
    )

with col2:

    st.metric(
        "Total Electricity Cost",
        f"₹ {round(total_cost, 2)}"
    )

with col3:

    st.metric(
        "Avg Power Cost / Part",
        f"₹ {round(avg_cost_per_part, 2)}"
    )

with col4:

    st.metric(
        "Avg Power Consumption / Part",
        f"{round(avg_power_per_part, 4)} kWh"
    )

# =========================================
# TOP ENERGY CONSUMING PARTS
# =========================================

st.subheader("Top Energy Consuming Parts")

top_energy = df.sort_values(
    by="power_consumption_kwh",
    ascending=False
)

st.dataframe(

    top_energy[[
        "part_no",
        "machine_tonnage",
        "schedule",
        "power_consumption_kwh",
        "electricity_cost"
    ]].head(20),

    use_container_width=True

)

# =========================================
# POWER CONSUMPTION CHART
# =========================================

st.subheader("Top Power Consumption Parts")

fig1 = px.bar(

    top_energy.head(10),

    x="part_no",
    y="power_consumption_kwh",

    title="Highest Energy Consuming Parts",

    text_auto=True

)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# =========================================
# ELECTRICITY COST ANALYSIS
# =========================================

st.subheader("Top Electricity Cost Parts")

fig2 = px.bar(

    top_energy.head(10),

    x="part_no",
    y="electricity_cost",

    title="Highest Electricity Cost Parts",

    text_auto=True

)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =========================================
# TONNAGE-WISE POWER ANALYSIS
# =========================================

st.subheader("Machine Tonnage-wise Energy Analysis")

tonnage_summary = df.groupby(
    "machine_tonnage"
)[[
    "power_consumption_kwh",
    "electricity_cost"
]].sum().reset_index()

fig3 = px.pie(

    tonnage_summary,

    names="machine_tonnage",
    values="power_consumption_kwh",

    title="Power Consumption by Machine Tonnage"

)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =========================================
# POWER EFFICIENCY
# =========================================

st.subheader("Power Efficient Parts")

efficient_parts = df.sort_values(
    by="power_cost_per_part"
)

st.dataframe(

    efficient_parts[[
        "part_no",
        "power_cost_per_part",
        "power_consumption_kwh"
    ]].head(20),

    use_container_width=True

)

# =========================================
# FULL DATA
# =========================================

st.subheader("Full Power Consumption Data")

st.dataframe(
    df,
    use_container_width=True
)

