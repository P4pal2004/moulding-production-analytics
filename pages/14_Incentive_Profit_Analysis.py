import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Production Incentive Profit Analysis",
    layout="wide"
)

st.title("Production Incentive vs Profit Analysis")

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
        "Could not detect correct Excel header row."
    )

    st.stop()

# ---------------------------------------------------
# SHOW DETECTED HEADER
# ---------------------------------------------------

st.sidebar.success(
    f"Header row detected successfully"
)

# ---------------------------------------------------
# REQUIRED COLUMNS
# ---------------------------------------------------

required_cols = [

    "part_no",

    "schedule",

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

# ---------------------------------------------------
# CREATE MISSING OPTIONAL COLUMNS
# ---------------------------------------------------

optional_cols = {

    "total_mfg_cost": 0,

    "shift_rate": 0,

    "manpoer_requirement": 1
}

for col, default_value in optional_cols.items():

    if col not in df.columns:

        df[col] = default_value

# ---------------------------------------------------
# CLEAN NUMERIC COLUMNS
# ---------------------------------------------------

numeric_cols = [

    "schedule",

    "total_mfg_cost",

    "shift_rate",

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
    subset=["schedule"]
)

# ---------------------------------------------------
# REMOVE ZERO SCHEDULE
# ---------------------------------------------------

df = df[
    df["schedule"] > 0
]

# ---------------------------------------------------
# IF MFG COST IS EMPTY CREATE APPROXIMATE COST
# ---------------------------------------------------

if df["total_mfg_cost"].sum() == 0:

    st.warning(
        "Manufacturing cost missing. Using estimated cost model."
    )

    df["total_mfg_cost"] = (

        df["schedule"] * 5
    )

# ---------------------------------------------------
# CURRENT VALUES
# ---------------------------------------------------

current_production = float(
    df["schedule"].sum()
)

current_mfg_cost = float(
    df["total_mfg_cost"].sum()
)

current_operators = float(
    df["manpoer_requirement"].sum()
)

# ---------------------------------------------------
# SAFETY CHECK
# ---------------------------------------------------

if current_production <= 0:

    st.error(
        "Schedule data invalid."
    )

    st.stop()

# ---------------------------------------------------
# SIDEBAR SETTINGS
# ---------------------------------------------------

st.sidebar.header(
    "Simulation Settings"
)

increase_percent = st.sidebar.slider(

    "Production Increase %",

    0,

    50,

    20
)

incentive_per_operator = st.sidebar.number_input(

    "Monthly Incentive Per Operator (₹)",

    value=3000
)

selling_margin_percent = st.sidebar.slider(

    "Selling Margin %",

    5,

    50,

    20
)

# ---------------------------------------------------
# FUTURE PRODUCTION
# ---------------------------------------------------

future_production = (

    current_production *

    (
        1 +
        increase_percent / 100
    )
)

# ---------------------------------------------------
# INCENTIVE COST
# ---------------------------------------------------

incentive_cost = (

    current_operators *

    incentive_per_operator
)

# ---------------------------------------------------
# CURRENT COST PER PART
# ---------------------------------------------------

current_cost_per_part = (

    current_mfg_cost /

    current_production
)

# ---------------------------------------------------
# FUTURE TOTAL COST
# ---------------------------------------------------

future_total_cost = (

    current_mfg_cost +

    incentive_cost
)

# ---------------------------------------------------
# FUTURE COST PER PART
# ---------------------------------------------------

future_cost_per_part = (

    future_total_cost /

    future_production
)

# ---------------------------------------------------
# SELLING PRICE
# ---------------------------------------------------

selling_price_per_part = (

    current_cost_per_part *

    (
        1 +
        selling_margin_percent / 100
    )
)

# ---------------------------------------------------
# CURRENT PROFIT
# ---------------------------------------------------

current_profit = (

    (
        selling_price_per_part -

        current_cost_per_part
    )

    * current_production
)

# ---------------------------------------------------
# FUTURE PROFIT
# ---------------------------------------------------

future_profit = (

    (
        selling_price_per_part -

        future_cost_per_part
    )

    * future_production
)

# ---------------------------------------------------
# PROFIT IMPROVEMENT
# ---------------------------------------------------

profit_improvement = (

    future_profit -

    current_profit
)

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

st.subheader(
    "Current vs Future Analysis"
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(

        "Current Production",

        f"{int(current_production):,}"
    )

with col2:

    st.metric(

        "Future Production",

        f"{int(future_production):,}",

        f"+{increase_percent}%"
    )

with col3:

    st.metric(

        "Current Cost / Part",

        f"₹ {round(current_cost_per_part,2)}"
    )

with col4:

    st.metric(

        "Future Cost / Part",

        f"₹ {round(future_cost_per_part,2)}"
    )

# ---------------------------------------------------
# PROFIT SECTION
# ---------------------------------------------------

col5, col6, col7 = st.columns(3)

with col5:

    st.metric(

        "Current Profit",

        f"₹ {int(current_profit):,}"
    )

with col6:

    st.metric(

        "Future Profit",

        f"₹ {int(future_profit):,}"
    )

with col7:

    st.metric(

        "Profit Improvement",

        f"₹ {int(profit_improvement):,}"
    )

# ---------------------------------------------------
# BUSINESS INTERPRETATION
# ---------------------------------------------------

st.subheader(
    "Business Interpretation"
)

if profit_improvement > 0:

    st.success(

        f'''
Increasing production by {increase_percent}%
with operator incentives is profitable.

Estimated Additional Profit:
₹ {int(profit_improvement):,}
'''
    )

else:

    st.error(

        f'''
Incentive cost is higher than profit gain.

Estimated Loss:
₹ {abs(int(profit_improvement)):,}
'''
    )

# ---------------------------------------------------
# CHART
# ---------------------------------------------------

chart_df = pd.DataFrame({

    "Scenario": [

        "Current",

        "Future"
    ],

    "Profit": [

        current_profit,

        future_profit
    ]
})

fig = px.bar(

    chart_df,

    x="Scenario",

    y="Profit",

    title="Current vs Future Profit Analysis"
)

st.plotly_chart(

    fig,

    use_container_width=True
)

# ---------------------------------------------------
# MACHINE ANALYSIS
# ---------------------------------------------------

st.subheader(
    "Machine-wise Analysis"
)

machine_df = (

    df.groupby("machine_tonnage")

    .agg({

        "schedule": "sum",

        "total_mfg_cost": "sum"
    })

    .reset_index()
)

machine_df["future_schedule"] = (

    machine_df["schedule"]

    *

    (
        1 +
        increase_percent / 100
    )

).astype(int)

machine_df["cost_per_part"] = (

    machine_df["total_mfg_cost"]

    /

    machine_df["schedule"]
)

st.dataframe(

    machine_df,

    use_container_width=True
)

# ---------------------------------------------------
# STRATEGIC RECOMMENDATIONS
# ---------------------------------------------------

st.subheader(
    "Strategic Recommendations"
)

st.markdown(

    f'''
### Key Findings

- Production Increase: **{increase_percent}%**
- Incentive Cost: **₹ {int(incentive_cost):,}**
- Current Cost / Part: **₹ {round(current_cost_per_part,2)}**
- Future Cost / Part: **₹ {round(future_cost_per_part,2)}**

### Industrial Insights

Increasing production while maintaining
stable overhead costs can:

✅ Reduce manufacturing cost per part

✅ Improve machine utilization

✅ Improve operator efficiency

✅ Improve plant productivity

✅ Increase profit margins

### Recommended Actions

✅ Incentive-based productivity improvement

✅ Reduce idle machine time

✅ Reduce rejection losses

✅ Improve OEE

✅ Improve attendance management

✅ Improve shift utilization
'''
)

