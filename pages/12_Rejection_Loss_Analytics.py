import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Rejection Analytics",
    layout="wide"
)

st.title("Rejection Loss & Quality Analytics")

# =========================================
# LOAD MONTHLY CLEANED DATA
# =========================================

production_df = pd.read_excel(
    "master_production_data.xlsx",
    engine="openpyxl"
)

# =========================================
# LOAD MASTER DATA
# =========================================

master_df = pd.read_excel(
    "MASTER DATA OF MOULDING.xlsx",
    header=2,
    engine="openpyxl"
)

# =========================================
# CLEAN COLUMN NAMES
# =========================================

production_df.columns = (

    production_df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")

)

master_df.columns = (

    master_df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("(", "")
    .str.replace(")", "")

)

# =========================================
# FIX MERGED CELLS
# =========================================

master_df = master_df.ffill()

# =========================================
# CLEAN PART NUMBERS
# =========================================

production_df["part_no"] = (

    production_df["part_no"]
    .astype(str)
    .str.strip()

)

master_df["part_no"] = (

    master_df["part_no"]
    .astype(str)
    .str.strip()

)

# =========================================
# REMOVE DUPLICATES
# =========================================

master_df = master_df.drop_duplicates(
    subset="part_no"
)

# =========================================
# MERGE DATA
# =========================================

df = pd.merge(

    production_df,

    master_df[[
        "part_no",
        "charge_weight_grams",
        "material_rate_kg",
        "machine_tonnage"
    ]],

    on="part_no",
    how="left"

)

# =========================================
# NUMERIC CONVERSION
# =========================================

numeric_cols = [

    "total_output",
    "rejection",
    "charge_weight_grams",
    "material_rate_kg"

]

for col in numeric_cols:

    df[col] = (

        df[col]
        .astype(str)
        .str.replace(",", "")
        .str.replace("₹", "")
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
    df["total_output"] > 0
]

# =========================================
# REJECTION %
# =========================================

df["rejection_percent"] = (

    df["rejection"]
    /
    df["total_output"]

) * 100

# =========================================
# QUALITY EFFICIENCY
# =========================================

df["quality_efficiency"] = (

    100
    -
    df["rejection_percent"]

)

# =========================================
# RM LOSS KG
# =========================================

df["rm_loss_kg"] = (

    df["charge_weight_grams"]
    *
    df["rejection"]

) / 1000

# =========================================
# REJECTION COST
# =========================================

df["rejection_cost"] = (

    df["rm_loss_kg"]
    *
    df["material_rate_kg"]

)

# =========================================
# KPI SECTION
# =========================================

total_production = df[
    "total_output"
].sum()

total_rejection = df[
    "rejection"
].sum()

overall_rejection_percent = (

    total_rejection
    /
    total_production

) * 100

total_rejection_cost = df[
    "rejection_cost"
].sum()

quality_efficiency = (

    100
    -
    overall_rejection_percent

)

# =========================================
# KPI DISPLAY
# =========================================

st.subheader("Rejection KPI Summary")

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
        "Overall Rejection %",
        f"{round(overall_rejection_percent, 2)} %"
    )

with col4:

    st.metric(
        "Quality Efficiency",
        f"{round(quality_efficiency, 2)} %"
    )

# =========================================
# REJECTION COST KPI
# =========================================

st.metric(
    "Total Rejection Loss Cost",
    f"₹ {round(total_rejection_cost, 2)}"
)

# =========================================
# TOP REJECTION PARTS
# =========================================

st.subheader("Top Rejection Parts")

top_rejection = df.sort_values(
    by="rejection",
    ascending=False
)

st.dataframe(

    top_rejection[[
        "part_no",
        "total_output",
        "rejection",
        "rejection_percent",
        "rejection_cost"
    ]].head(20),

    use_container_width=True

)

# =========================================
# TOP REJECTION CHART
# =========================================

st.subheader("Highest Rejection Parts")

fig1 = px.bar(

    top_rejection.head(10),

    x="part_no",
    y="rejection",

    title="Top Rejection Parts",

    text_auto=True

)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# =========================================
# REJECTION COST CHART
# =========================================

st.subheader("Highest Rejection Cost")

fig2 = px.bar(

    top_rejection.head(10),

    x="part_no",
    y="rejection_cost",

    title="Highest Rejection Cost Parts",

    text_auto=True

)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =========================================
# TONNAGE-WISE REJECTION
# =========================================

st.subheader("Machine Tonnage-wise Rejection")

tonnage_rejection = df.groupby(
    "machine_tonnage"
)[[
    "rejection",
    "rejection_cost"
]].sum().reset_index()

fig3 = px.pie(

    tonnage_rejection,

    names="machine_tonnage",
    values="rejection",

    title="Rejection by Machine Tonnage"

)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =========================================
# BEST QUALITY PARTS
# =========================================

st.subheader("Best Quality Parts")

best_quality = df.sort_values(
    by="rejection_percent"
)

st.dataframe(

    best_quality[[
        "part_no",
        "rejection_percent",
        "quality_efficiency"
    ]].head(20),

    use_container_width=True

)

# =========================================
# FULL DATA
# =========================================

st.subheader("Full Rejection Analytics Data")

st.dataframe(
    df,
    use_container_width=True
)

