import streamlit as st
import pandas as pd

st.title("Machine Capacity Analytics")

# =====================================
# LOAD MASTER DATA
# =====================================

df = pd.read_excel(
    "MASTER DATA OF MOULDING.xlsx",
    header=2,
    engine="openpyxl"
)

# =====================================
# CLEAN COLUMN NAMES
# =====================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# =====================================
# REQUIRED COLUMNS CHECK
# =====================================

required_cols = [

    "part_no",
    "machine_tonnage",
    "schedule",
    "shift_output_moulding"

]

missing_cols = [

    col for col in required_cols
    if col not in df.columns

]

if missing_cols:

    st.error(
        f"Missing columns: {missing_cols}"
    )

    st.write("Available Columns:")
    st.write(df.columns.tolist())

    st.stop()

# =====================================
# NUMERIC CONVERSION
# =====================================

df["schedule"] = pd.to_numeric(
    df["schedule"],
    errors="coerce"
).fillna(0)

df["shift_output_moulding"] = pd.to_numeric(
    df["shift_output_moulding"],
    errors="coerce"
).fillna(0)

# =====================================
# REMOVE ZERO OUTPUT
# =====================================

df = df[
    df["shift_output_moulding"] > 0
]

# =====================================
# REQUIRED SHIFTS
# =====================================

df["required_shifts"] = (

    df["schedule"]
    /
    df["shift_output_moulding"]

)

# =====================================
# LOAD MACHINE CONFIG
# =====================================

config_df = pd.read_excel(
    "machine_config.xlsx",
    engine="openpyxl"
)

# =====================================
# CLEAN CONFIG COLUMNS
# =====================================

config_df.columns = (

    config_df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")

)

# =====================================
# REQUIRED CONFIG COLUMNS
# =====================================

config_required = [

    "machine_tonnage",
    "machine_count",
    "daily_shifts",
    "working_days"

]

missing_config = [

    col for col in config_required
    if col not in config_df.columns

]

if missing_config:

    st.error(
        f"Missing config columns: {missing_config}"
    )

    st.write(config_df.columns.tolist())

    st.stop()

# =====================================
# AVAILABLE MONTHLY SHIFTS
# =====================================

config_df["available_shifts"] = (

    config_df["machine_count"]
    *
    config_df["daily_shifts"]
    *
    config_df["working_days"]

)

# =====================================
# MACHINE SUMMARY
# =====================================

machine_summary = df.groupby(
    "machine_tonnage"
).agg({

    "required_shifts": "sum",
    "schedule": "sum"

}).reset_index()

# =====================================
# MERGE CONFIG
# =====================================

machine_summary = pd.merge(

    machine_summary,

    config_df[[
        "machine_tonnage",
        "machine_count",
        "daily_shifts",
        "working_days",
        "available_shifts"
    ]],

    on="machine_tonnage",
    how="left"

)

# =====================================
# UTILISATION %
# =====================================

machine_summary["utilisation_%"] = (

    machine_summary["required_shifts"]
    /
    machine_summary["available_shifts"]

) * 100

# =====================================
# ROUND VALUES
# =====================================

machine_summary["required_shifts"] = (
    machine_summary["required_shifts"]
    .round(2)
)

machine_summary["utilisation_%"] = (
    machine_summary["utilisation_%"]
    .round(2)
)

# =====================================
# KPI SECTION
# =====================================

total_required = machine_summary[
    "required_shifts"
].sum()

total_schedule = machine_summary[
    "schedule"
].sum()

avg_utilisation = machine_summary[
    "utilisation_%"
].mean()

overloaded_count = len(

    machine_summary[
        machine_summary["utilisation_%"] > 100
    ]

)

# =====================================
# DISPLAY KPIs
# =====================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total Schedule",
        int(total_schedule)
    )

with col2:

    st.metric(
        "Required Shifts",
        round(total_required, 2)
    )

with col3:

    st.metric(
        "Average Utilisation %",
        round(avg_utilisation, 2)
    )

with col4:

    st.metric(
        "Overloaded Machines",
        overloaded_count
    )

# =====================================
# MACHINE SUMMARY TABLE
# =====================================

st.subheader("Machine-wise Capacity Summary")

st.dataframe(machine_summary)

# =====================================
# OVERLOADED MACHINES
# =====================================

st.subheader("Overloaded Machines")

overloaded = machine_summary[

    machine_summary["utilisation_%"] > 100

]

st.dataframe(overloaded)

# =====================================
# UNDERLOADED MACHINES
# =====================================

st.subheader("Underloaded Machines")

underloaded = machine_summary[

    machine_summary["utilisation_%"] < 50

]

st.dataframe(underloaded)

# =====================================
# PART DETAILS
# =====================================

st.subheader("Part-wise Shift Requirement")

part_details = df[[

    "part_no",
    "machine_tonnage",
    "schedule",
    "shift_output_moulding",
    "required_shifts"

]]

part_details["required_shifts"] = (
    part_details["required_shifts"]
    .round(2)
)

st.dataframe(part_details)

