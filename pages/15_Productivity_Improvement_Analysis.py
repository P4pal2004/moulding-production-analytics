import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Productivity & Cost Optimization",
    layout="wide"
)

st.title("Productivity Improvement & Manufacturing Cost Optimization")

# ---------------------------------------------------
# LOAD EXCEL FILE
# ---------------------------------------------------

header_found = False

for header_row in [0, 1, 2, 3, 4]:

    try:

        temp_df = pd.read_excel(
            "MASTER DATA OF MOULDING.xlsx",
            header=header_row
        )

        temp_df.columns = (

            temp_df.columns

            .astype(str)

            .str.strip()

            .str.lower()

            .str.replace(" ", "_")

            .str.replace("\n", "")

            .str.replace("-", "_")
        )

        if "schedule" in temp_df.columns:

            df = temp_df.copy()

            header_found = True

            break

    except:

        pass

# ---------------------------------------------------
# HEADER CHECK
# ---------------------------------------------------

if not header_found:

    st.error(
        "Could not detect Excel headers."
    )

    st.stop()

# ---------------------------------------------------
# REQUIRED COLUMNS
# ---------------------------------------------------

required_cols = [

    "part_no",

    "schedule",

    "shift_output_of_8_hrs",

    "machine_tonnage",

    "motor_hp",

    "heater_watt"
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
# OPTIONAL COLUMNS
# ---------------------------------------------------

optional_cols = {

    "total_mfg_cost": 0,

    "manpoer_requirement": 1
}

for col, default_value in optional_cols.items():

    if col not in df.columns:

        df[col] = default_value

# ---------------------------------------------------
# NUMERIC CONVERSION
# ---------------------------------------------------

numeric_cols = [

    "schedule",

    "shift_output_of_8_hrs",

    "motor_hp",

    "heater_watt",

    "total_mfg_cost",

    "manpoer_requirement"
]

for col in numeric_cols:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# ---------------------------------------------------
# REMOVE INVALID ROWS
# ---------------------------------------------------

df = df.dropna(
    subset=[
        "schedule",
        "shift_output_of_8_hrs"
    ]
)

df = df[
    (df["schedule"] > 0)
    &
    (df["shift_output_of_8_hrs"] > 0)
]

# ---------------------------------------------------
# SIDEBAR SETTINGS
# ---------------------------------------------------

st.sidebar.header(
    "Optimization Settings"
)

productivity_increase = st.sidebar.slider(

    "Production Improvement %",

    0,

    50,

    20
)

electricity_rate = st.sidebar.number_input(

    "Electricity Rate ₹/kWh",

    value=8
)

monthly_incentive = st.sidebar.number_input(

    "Monthly Incentive Cost ₹",

    value=50000
)

# ---------------------------------------------------
# MACHINE CONFIGURATION
# ---------------------------------------------------

machine_config = {

    "100T": 6,

    "150T": 5
}

working_days = 26

daily_shifts = 2

available_shifts = (

    sum(machine_config.values())

    * working_days

    * daily_shifts
)

# ---------------------------------------------------
# CURRENT REQUIRED SHIFTS
# ---------------------------------------------------

df["required_shifts"] = (

    df["schedule"]

    /

    df["shift_output_of_8_hrs"]
)

current_required_shifts = (

    df["required_shifts"].sum()
)

# ---------------------------------------------------
# IMPROVED OUTPUT
# ---------------------------------------------------

df["improved_output"] = (

    df["shift_output_of_8_hrs"]

    *

    (
        1 +
        productivity_increase / 100
    )
)

# ---------------------------------------------------
# NEW REQUIRED SHIFTS
# ---------------------------------------------------

df["new_required_shifts"] = (

    df["schedule"]

    /

    df["improved_output"]
)

new_required_shifts = (

    df["new_required_shifts"].sum()
)

# ---------------------------------------------------
# SHIFT SAVING
# ---------------------------------------------------

shift_saving = (

    current_required_shifts -

    new_required_shifts
)

# ---------------------------------------------------
# MACHINE RUN HOURS
# ---------------------------------------------------

current_runtime_hours = (

    current_required_shifts * 8
)

new_runtime_hours = (

    new_required_shifts * 8
)

runtime_saved = (

    current_runtime_hours -

    new_runtime_hours
)

# ---------------------------------------------------
# POWER CALCULATION
# ---------------------------------------------------

df["motor_kw"] = (

    df["motor_hp"] * 0.746
)

df["heater_kw"] = (

    df["heater_watt"] / 1000
)

df["total_kw"] = (

    df["motor_kw"]

    +

    df["heater_kw"]
)

average_kw = (

    df["total_kw"].mean()
)

# ---------------------------------------------------
# POWER CONSUMPTION
# ---------------------------------------------------

current_power_units = (

    average_kw *

    current_runtime_hours
)

new_power_units = (

    average_kw *

    new_runtime_hours
)

power_units_saved = (

    current_power_units -

    new_power_units
)

# ---------------------------------------------------
# POWER COST SAVING
# ---------------------------------------------------

power_cost_saving = (

    power_units_saved *

    electricity_rate
)

# ---------------------------------------------------
# CURRENT COST
# ---------------------------------------------------

if df["total_mfg_cost"].sum() == 0:

    current_total_cost = (

        current_power_units *

        electricity_rate
    )

else:

    current_total_cost = (

        df["total_mfg_cost"].sum()
    )

# ---------------------------------------------------
# OVERHEAD SAVING
# ---------------------------------------------------

overhead_saving = (

    shift_saving * 2500
)

# ---------------------------------------------------
# FUTURE COST
# ---------------------------------------------------

future_total_cost = (

    current_total_cost

    -

    power_cost_saving

    -

    overhead_saving

    +

    monthly_incentive
)

# ---------------------------------------------------
# PRODUCTION
# ---------------------------------------------------

current_total_production = (

    df["schedule"].sum()
)

future_production = (

    current_total_production

    *

    (
        1 +
        productivity_increase / 100
    )
)

# ---------------------------------------------------
# COST PER PART
# ---------------------------------------------------

current_cost_per_part = (

    current_total_cost /

    current_total_production
)

future_cost_per_part = (

    future_total_cost /

    future_production
)

cost_reduction = (

    current_cost_per_part -

    future_cost_per_part
)

# ---------------------------------------------------
# UTILIZATION
# ---------------------------------------------------

current_utilization = (

    current_required_shifts /

    available_shifts
) * 100

new_utilization = (

    new_required_shifts /

    available_shifts
) * 100

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

st.subheader(
    "Shift & Utilization Analysis"
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Available Shifts",
        round(available_shifts,2)
    )

with col2:

    st.metric(
        "Current Required Shifts",
        round(current_required_shifts,2)
    )

with col3:

    st.metric(
        "New Required Shifts",
        round(new_required_shifts,2)
    )

with col4:

    st.metric(
        "Shift Saving",
        round(shift_saving,2)
    )

# ---------------------------------------------------
# COST KPI
# ---------------------------------------------------

st.subheader(
    "Cost Optimization"
)

col5, col6, col7, col8 = st.columns(4)

with col5:

    st.metric(
        "Current Cost / Part",
        f"₹ {round(current_cost_per_part,2)}"
    )

with col6:

    st.metric(
        "Future Cost / Part",
        f"₹ {round(future_cost_per_part,2)}"
    )

with col7:

    st.metric(
        "Cost Reduction",
        f"₹ {round(cost_reduction,2)}"
    )

with col8:

    st.metric(
        "Power Cost Saving",
        f"₹ {int(power_cost_saving):,}"
    )

# ---------------------------------------------------
# UTILIZATION KPI
# ---------------------------------------------------

st.subheader(
    "Machine Utilization"
)

col9, col10, col11 = st.columns(3)

with col9:

    st.metric(
        "Current Utilization %",
        f"{round(current_utilization,2)}%"
    )

with col10:

    st.metric(
        "New Utilization %",
        f"{round(new_utilization,2)}%"
    )

with col11:

    st.metric(
        "Runtime Hours Saved",
        round(runtime_saved,2)
    )

# ---------------------------------------------------
# INDUSTRIAL ANALYSIS
# ---------------------------------------------------

st.subheader(
    "Industrial Analysis"
)

if new_required_shifts <= available_shifts:

    st.success(
        """
        Schedule can be completed
        within available shifts after
        productivity improvement.
        """
    )

else:

    st.error(
        """
        Extra shifts are still required
        even after productivity increase.
        """
    )

if future_cost_per_part < current_cost_per_part:

    st.success(
        """
        Productivity incentive strategy
        reduces manufacturing cost.
        """
    )

else:

    st.warning(
        """
        Incentive cost is higher than
        productivity savings.
        """
    )

# ---------------------------------------------------
# CHART
# ---------------------------------------------------

chart_df = pd.DataFrame({

    "Scenario": [

        "Current",

        "Improved"
    ],

    "Required Shifts": [

        current_required_shifts,

        new_required_shifts
    ],

    "Cost Per Part": [

        current_cost_per_part,

        future_cost_per_part
    ]
})

fig = px.bar(

    chart_df,

    x="Scenario",

    y="Required Shifts",

    title="Shift Requirement Comparison"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------------------------
# MACHINE ANALYSIS
# ---------------------------------------------------

st.subheader(
    "Part-wise Shift Analysis"
)

display_df = df[[

    "part_no",

    "machine_tonnage",

    "schedule",

    "required_shifts",

    "new_required_shifts"
]]

st.dataframe(
    display_df,
    use_container_width=True
)

# ---------------------------------------------------
# FINAL INSIGHTS
# ---------------------------------------------------

st.subheader(
    "Strategic Manufacturing Insights"
)

st.markdown(

    f"""
### Key Benefits After Productivity Improvement

✅ Shift Saving = **{round(shift_saving,2)}**

✅ Runtime Reduction = **{round(runtime_saved,2)} hrs**

✅ Power Saving = **₹ {int(power_cost_saving):,}**

✅ Overhead Reduction = **₹ {int(overhead_saving):,}**

✅ Cost Reduction / Part = **₹ {round(cost_reduction,2)}**

### Industrial Conclusion

Increasing operator productivity by
**{productivity_increase}%**
through incentives:

- reduces runtime
- reduces power consumption
- improves machine utilization
- reduces overhead allocation
- reduces manufacturing cost
- improves plant efficiency

This is a beneficial industrial strategy.
"""
)

