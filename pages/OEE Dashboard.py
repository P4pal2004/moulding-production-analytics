import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(

    page_title="Industrial OEE Dashboard",

    layout="wide"
)

st.title(
    "Overall Equipment Effectiveness (OEE) Dashboard"
)

# ---------------------------------------------------
# LOAD EXCEL
# ---------------------------------------------------

header_found = False

for header_row in [0,1,2,3,4]:

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

if not header_found:

    st.error(
        "Could not detect Excel headers"
    )

    st.stop()

# ---------------------------------------------------
# REQUIRED COLUMNS
# ---------------------------------------------------

required_cols = [

    "part_no",

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

# ---------------------------------------------------
# OPTIONAL REJECTION COLUMNS
# ---------------------------------------------------

if "rejection" not in df.columns:

    df["rejection"] = 0

if "rejection_qty" not in df.columns:

    df["rejection_qty"] = 0

# ---------------------------------------------------
# NUMERIC CONVERSION
# ---------------------------------------------------

numeric_cols = [

    "schedule",

    "shift_output_moulding",

    "rejection",

    "rejection_qty"
]

for col in numeric_cols:

    df[col] = pd.to_numeric(

        df[col],

        errors="coerce"
    )

# ---------------------------------------------------
# CLEAN DATA
# ---------------------------------------------------

df = df.dropna(

    subset=[

        "schedule",

        "shift_output_moulding"
    ]
)

df = df[

    (df["schedule"] > 0)

    &

    (df["shift_output_moulding"] > 0)
]

# ---------------------------------------------------
# MACHINE CONFIGURATION
# ---------------------------------------------------

machine_config = {

    "100T": 6,

    "150T": 5
}

working_days = 26

daily_shifts = 2

shift_hours = 12

total_machines = sum(

    machine_config.values()
)

# ---------------------------------------------------
# PLANNED PRODUCTION TIME
# ---------------------------------------------------

planned_shift_capacity = (

    total_machines

    * working_days

    * daily_shifts
)

planned_production_hours = (

    planned_shift_capacity

    * shift_hours
)

# ---------------------------------------------------
# REQUIRED SHIFTS
# ---------------------------------------------------

df["required_shifts"] = (

    df["schedule"]

    /

    df["shift_output_moulding"]
)

actual_required_shifts = (

    df["required_shifts"].sum()
)

# ---------------------------------------------------
# INDUSTRIAL DOWNTIME ASSUMPTIONS
# ---------------------------------------------------

# breakdown loss
breakdown_loss_percent = 5

# setup/changeover loss
setup_loss_percent = 5

# minor stoppage loss
minor_stop_loss_percent = 5

total_availability_loss = (

    breakdown_loss_percent

    +

    setup_loss_percent

    +

    minor_stop_loss_percent
)

# ---------------------------------------------------
# AVAILABILITY
# ---------------------------------------------------

availability = (

    100 - total_availability_loss
)

# ---------------------------------------------------
# PERFORMANCE LOSS
# ---------------------------------------------------

# Industrial speed loss assumption

speed_loss_percent = 10

performance = (

    100 - speed_loss_percent
)

# ---------------------------------------------------
# QUALITY
# ---------------------------------------------------

total_output = (

    df["schedule"].sum()
)

total_rejection = (

    df["rejection"].sum()

    +

    df["rejection_qty"].sum()
)

good_parts = (

    total_output - total_rejection
)

if total_output > 0:

    quality = (

        good_parts

        /

        total_output
    ) * 100

else:

    quality = 100

quality = max(

    0,

    min(quality, 100)
)

# ---------------------------------------------------
# OEE
# ---------------------------------------------------

oee = (

    availability

    *

    performance

    *

    quality

) / 10000

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

st.subheader(
    "Industrial OEE KPI Summary"
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(

        "Availability %",

        round(availability,2)
    )

with col2:

    st.metric(

        "Performance %",

        round(performance,2)
    )

with col3:

    st.metric(

        "Quality %",

        round(quality,2)
    )

with col4:

    st.metric(

        "OEE %",

        round(oee,2)
    )

# ---------------------------------------------------
# INDUSTRIAL BENCHMARK
# ---------------------------------------------------

st.subheader(
    "Industrial OEE Benchmark"
)

if oee >= 85:

    st.success(
        "World Class Manufacturing"
    )

elif oee >= 70:

    st.warning(
        "Good Industrial Performance"
    )

elif oee >= 60:

    st.warning(
        "Average Industrial Performance"
    )

else:

    st.error(
        "Improvement Required"
    )

# ---------------------------------------------------
# OEE BREAKDOWN
# ---------------------------------------------------

st.subheader(
    "OEE Breakdown"
)

oee_df = pd.DataFrame({

    "Metric": [

        "Availability",

        "Performance",

        "Quality",

        "OEE"
    ],

    "Value": [

        availability,

        performance,

        quality,

        oee
    ]
})

fig = px.bar(

    oee_df,

    x="Metric",

    y="Value",

    text="Value",

    title="Industrial OEE Breakdown"
)

st.plotly_chart(

    fig,

    use_container_width=True
)

# ---------------------------------------------------
# OEE LOSS ANALYSIS
# ---------------------------------------------------

st.subheader(
    "OEE Loss Analysis"
)

loss_df = pd.DataFrame({

    "Loss Type": [

        "Breakdown Loss",

        "Setup Loss",

        "Minor Stop Loss",

        "Speed Loss",

        "Rejection Loss"
    ],

    "Loss %": [

        breakdown_loss_percent,

        setup_loss_percent,

        minor_stop_loss_percent,

        speed_loss_percent,

        100 - quality
    ]
})

fig2 = px.pie(

    loss_df,

    names="Loss Type",

    values="Loss %",

    title="Manufacturing Loss Distribution"
)

st.plotly_chart(

    fig2,

    use_container_width=True
)

# ---------------------------------------------------
# MACHINE ANALYSIS
# ---------------------------------------------------

st.subheader(
    "Machine-wise Production Analysis"
)

machine_df = (

    df.groupby("machine_tonnage")

    .agg({

        "schedule": "sum",

        "shift_output_moulding": "mean"
    })

    .reset_index()
)

machine_df["required_shifts"] = (

    machine_df["schedule"]

    /

    machine_df["shift_output_moulding"]
)

st.dataframe(

    machine_df,

    use_container_width=True
)

# ---------------------------------------------------
# PART-WISE ANALYSIS
# ---------------------------------------------------

st.subheader(
    "Part-wise Shift Requirement"
)

display_df = df[[

    "part_no",

    "machine_tonnage",

    "schedule",

    "shift_output_moulding",

    "required_shifts"
]]

st.dataframe(

    display_df,

    use_container_width=True
)

# ---------------------------------------------------
# INDUSTRIAL INSIGHTS
# ---------------------------------------------------

st.subheader(
    "Industrial Manufacturing Insights"
)

st.markdown(

    f"""
### Current Plant Performance

✅ Availability = {round(availability,2)}%

✅ Performance = {round(performance,2)}%

✅ Quality = {round(quality,2)}%

✅ OEE = {round(oee,2)}%

---

### Industrial Meaning

- Availability losses indicate downtime.
- Performance losses indicate slower production.
- Quality losses indicate rejection.
- OEE indicates total manufacturing efficiency.

---

### Main Cost Reduction Opportunities

✅ Reduce breakdowns

✅ Reduce mould setup time

✅ Reduce operator idle time

✅ Improve production speed

✅ Reduce rejection

✅ Improve machine utilization

✅ Improve preventive maintenance

---

### Industrial Benchmark

| OEE % | Meaning |
|---|---|
| 85%+ | World Class |
| 70-85% | Good |
| 60-70% | Average |
| Below 60% | Improvement Required |

---

### Current Factory Status

Your current factory efficiency is approximately:

# {round(oee,2)}% OEE
"""
)

