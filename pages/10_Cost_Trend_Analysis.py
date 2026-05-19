import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Cost Trend Analysis",
    layout="wide"
)

st.title("Industrial Cost Trend Analytics")

# =====================================
# LOAD DATA
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
    .str.replace("(", "")
    .str.replace(")", "")

)

# =====================================
# FIX MERGED CELLS
# =====================================

df = df.ffill()

# =====================================
# REQUIRED COLUMNS
# =====================================

required_cols = [

    "part_no",
    "material_rate_kg",
    "charge_weight_grams",
    "shift_rate",
    "shift_output_moulding",
    "deflashing_rate",
    "ins_and_packing",
    "schedule"

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

# =====================================
# NUMERIC CONVERSION
# =====================================

numeric_cols = required_cols[1:]

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

# =====================================
# REMOVE INVALID ROWS
# =====================================

df = df[
    df["schedule"] > 0
]

# =====================================
# REMOVE DUPLICATE PARTS
# =====================================

df["part_no"] = (

    df["part_no"]
    .astype(str)
    .str.strip()

)

df = df.drop_duplicates(
    subset="part_no"
)

# =====================================
# REQUIRED RM KG
# =====================================

df["required_rm_kg"] = (

    df["charge_weight_grams"]
    *
    df["schedule"]

) / 1000

# =====================================
# RM COST
# =====================================

df["rm_cost"] = (

    df["required_rm_kg"]
    *
    df["material_rate_kg"]

)

# =====================================
# REQUIRED SHIFTS
# =====================================

df["required_shifts"] = (

    df["schedule"]
    /
    df["shift_output_moulding"]

)

df["required_shifts"] = (

    df["required_shifts"]
    .fillna(0)

)

# =====================================
# MOULDING COST
# =====================================

df["moulding_cost"] = (

    df["required_shifts"]
    *
    df["shift_rate"]

)

# =====================================
# DEFLASHING COST
# =====================================

df["deflashing_cost"] = (

    df["schedule"]
    *
    df["deflashing_rate"]

)

# =====================================
# PACKING COST
# =====================================

df["packing_cost"] = (

    df["schedule"]
    *
    df["ins_and_packing"]

)

# =====================================
# TOTAL MANUFACTURING COST
# =====================================

df["total_manufacturing_cost"] = (

    df["rm_cost"]
    +
    df["moulding_cost"]
    +
    df["deflashing_cost"]
    +
    df["packing_cost"]

)

# =====================================
# COST PER PART
# =====================================

df["cost_per_part"] = (

    df["total_manufacturing_cost"]
    /
    df["schedule"]

)

# =====================================
# KPI SUMMARY
# =====================================

total_rm = df[
    "required_rm_kg"
].sum()

total_rm_cost = df[
    "rm_cost"
].sum()

total_mfg_cost = df[
    "total_manufacturing_cost"
].sum()

avg_cost = df[
    "cost_per_part"
].mean()

# =====================================
# KPI DISPLAY
# =====================================

st.subheader("Cost KPI Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total RM Required (KG)",
        round(total_rm, 2)
    )

with col2:

    st.metric(
        "Total RM Cost",
        f"₹ {round(total_rm_cost, 2)}"
    )

with col3:

    st.metric(
        "Total Manufacturing Cost",
        f"₹ {round(total_mfg_cost, 2)}"
    )

with col4:

    st.metric(
        "Average Cost / Part",
        f"₹ {round(avg_cost, 2)}"
    )

# =====================================
# TOP COST PARTS
# =====================================

st.subheader("Highest Manufacturing Cost Parts")

top_cost = df.sort_values(
    by="total_manufacturing_cost",
    ascending=False
)

st.dataframe(

    top_cost[[
        "part_no",
        "schedule",
        "rm_cost",
        "moulding_cost",
        "deflashing_cost",
        "packing_cost",
        "total_manufacturing_cost"
    ]].head(20),

    use_container_width=True

)

# =====================================
# COST BREAKDOWN PIE CHART
# =====================================

st.subheader("Manufacturing Cost Breakdown")

cost_breakdown = pd.DataFrame({

    "Cost Type": [

        "RM Cost",
        "Moulding Cost",
        "Deflashing Cost",
        "Packing Cost"

    ],

    "Amount": [

        df["rm_cost"].sum(),
        df["moulding_cost"].sum(),
        df["deflashing_cost"].sum(),
        df["packing_cost"].sum()

    ]

})

fig1 = px.pie(

    cost_breakdown,

    names="Cost Type",
    values="Amount",

    title="Cost Contribution"

)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# =====================================
# TOP RM COST PARTS
# =====================================

st.subheader("Top RM Cost Parts")

rm_parts = df.sort_values(
    by="rm_cost",
    ascending=False
)

fig2 = px.bar(

    rm_parts.head(10),

    x="part_no",
    y="rm_cost",

    title="Top RM Cost Parts",

    text_auto=True

)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =====================================
# COST PER PART ANALYSIS
# =====================================

st.subheader("Highest Cost Per Part")

cost_per_part = df.sort_values(
    by="cost_per_part",
    ascending=False
)

st.dataframe(

    cost_per_part[[
        "part_no",
        "cost_per_part"
    ]].head(20),

    use_container_width=True

)

# =====================================
# FULL DATA
# =====================================

st.subheader("Full Cost Analysis Data")

st.dataframe(
    df,
    use_container_width=True
)

