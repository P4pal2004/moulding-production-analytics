import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------
st.set_page_config(
    page_title="Moulding Planning Dashboard",
    layout="wide"
)
st.title("Moulding Production Planning System")

st.subheader("Manufacturing Analytics Dashboard")
st.sidebar.title("Production Planning")

st.sidebar.markdown("---")

# ---------------------------------------------------
# READ EXCEL
# ---------------------------------------------------

master_df = pd.read_excel(
    "MASTER DATA OF MOULDING.xlsx",
    header=2
)

# ---------------------------------------------------
# FILL MERGED CELLS
# ---------------------------------------------------

master_df['MATERIAL RATE KG'] = (
    master_df['MATERIAL RATE KG']
    .ffill()
)

# ---------------------------------------------------
# CONVERT NUMERIC COLUMNS
# ---------------------------------------------------

numeric_columns = [
    'Charge Weight (Grams)',
    'shift output moulding',
    'SHIFT RATE',
    'MOTOR HP',
    'HEATER WATT',
    'MATERIAL RATE KG',
    'DEFLASHING RATE',
    'shift output of 8 hrs',
    'INS AND PACKING',
    'shift output for packing',
    'SCHEDULE'
]

for col in numeric_columns:

    master_df[col] = pd.to_numeric(
        master_df[col],
        errors='coerce'
    )

# ---------------------------------------------------
# RM REQUIRED KG
# ---------------------------------------------------

master_df['RM Required KG'] = (
    master_df['SCHEDULE'] *
    master_df['Charge Weight (Grams)']
) / 1000

# ---------------------------------------------------
# RM COST
# ---------------------------------------------------

master_df['RM Cost'] = (
    master_df['RM Required KG'] *
    master_df['MATERIAL RATE KG']
)

# ---------------------------------------------------
# REQUIRED SHIFTS
# ---------------------------------------------------

master_df['Required Shifts'] = (
    master_df['SCHEDULE'] /
    master_df['shift output moulding']
)

# ---------------------------------------------------
# AVAILABLE SHIFTS
# ---------------------------------------------------

master_df['Available Shifts'] = (
    master_df['machine tonnage']
    .map({
        '100T': 312,
        '150T': 260
    })
)

# ---------------------------------------------------
# UTILISATION %
# ---------------------------------------------------

master_df['Utilisation %'] = (
    master_df['Required Shifts'] /
    master_df['Available Shifts']
) * 100

# ---------------------------------------------------
# UTILISATION STATUS
# ---------------------------------------------------

master_df['Utilisation Status'] = (
    master_df['Utilisation %']
    .apply(
        lambda x:
        'Underloaded' if x < 70
        else 'Normal' if x <= 100
        else 'Overloaded'
    )
)

# ---------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------

total_rm = master_df['RM Required KG'].sum()

total_rm_cost = master_df['RM Cost'].sum()

total_required_shifts = (
    master_df['Required Shifts']
    .sum()
)

total_available_shifts = 312 + 260

plant_utilisation = (
    total_required_shifts /
    total_available_shifts
) * 100

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------

col1, col2, col3, col4 = st.columns(
    [1,1,1,1]
)

with col1:
    st.metric(
        "Total RM Required (KG)",
        round(total_rm, 2)
    )

with col2:
    st.metric(
        "Total RM Cost",
        round(total_rm_cost, 2)
    )

with col3:
    st.metric(
        "Plant Utilisation %",
        round(plant_utilisation, 2)
    )

with col4:
    st.metric(
        "Total Required Shifts",
        round(total_required_shifts, 2)
    )

# ---------------------------------------------------
# CREATE OUTPUT EXCEL
# ---------------------------------------------------

output_file = "Moulding_Planning_Output.xlsx"

with pd.ExcelWriter(output_file) as writer:

    master_df.to_excel(
        writer,
        sheet_name='Planning',
        index=False
    )

# ---------------------------------------------------
# SIDEBAR FILTER
# ---------------------------------------------------

machine_filter = st.sidebar.selectbox(
    "Select Machine",
    ['All', '100T', '150T']
)

# ---------------------------------------------------
# FILTER DATAFRAME
# ---------------------------------------------------

if machine_filter != 'All':

    filtered_df = master_df[
        master_df['machine tonnage'] == machine_filter
    ]

else:

    filtered_df = master_df

# ---------------------------------------------------
# SHOW IMPORTANT COLUMNS
# ---------------------------------------------------
st.markdown("## Part-wise Planning")
st.subheader("Part-wise Planning Summary")

st.dataframe(
    filtered_df[
        [
            'Part No',
            'Mould No',
            'machine tonnage',
            'SCHEDULE',
            'RM Required KG',
            'RM Cost',
            'Required Shifts',
            'Available Shifts',
            'Utilisation %',
            
        ]
    ]
)

# ---------------------------------------------------
# UTILISATION CHART
# ---------------------------------------------------

fig = px.bar(
    filtered_df,
    x='Part No',
    y='Utilisation %',
    color='machine tonnage',
    title='Machine Utilisation'
)

st.plotly_chart(fig)

# ---------------------------------------------------
# MOULD-WISE SUMMARY
# ---------------------------------------------------

mould_summary = (
    master_df
    .groupby(
        [
            'Mould No',
            'machine tonnage'
        ],
        as_index=False
    )
    .agg({
        'SCHEDULE': 'sum',
        'RM Required KG': 'sum',
        'Required Shifts': 'sum'
    })
)

# ---------------------------------------------------
# MOULD AVAILABLE SHIFTS
# ---------------------------------------------------

mould_summary['Available Shifts'] = (
    mould_summary['machine tonnage']
    .map({
        '100T': 312,
        '150T': 260
    })
)

# ---------------------------------------------------
# MOULD UTILISATION %
# ---------------------------------------------------

mould_summary['Utilisation %'] = (
    mould_summary['Required Shifts'] /
    mould_summary['Available Shifts']
) * 100

# ---------------------------------------------------
# MOULD UTILISATION STATUS
# ---------------------------------------------------

mould_summary['Utilisation Status'] = (
    mould_summary['Utilisation %']
    .apply(
        lambda x:
        'Underloaded' if x < 70
        else 'Normal' if x <= 100
        else 'Overloaded'
    )
)

# ---------------------------------------------------
# SHOW MOULD SUMMARY
# ---------------------------------------------------
st.markdown("## Mould-wise Analytics")
st.subheader("Mould-wise Summary")

st.dataframe(
    mould_summary[
        [
            'Mould No',
            'machine tonnage',
            'SCHEDULE',
            'RM Required KG',
            'Required Shifts',
            'Available Shifts',
            'Utilisation %',
            'Utilisation Status'
        ]
    ]
)

# ---------------------------------------------------
# MOULD UTILISATION CHART
# ---------------------------------------------------

mould_fig = px.bar(
    mould_summary,
    x='Mould No',
    y='Utilisation %',
    color='machine tonnage',
    title='Mould-wise Utilisation'
)

st.plotly_chart(mould_fig)
# ---------------------------------------------------
# MACHINE-WISE SUMMARY
# ---------------------------------------------------
st.markdown("## Machine Capacity Analysis")
machine_summary = (
    master_df
    .groupby(
        'machine tonnage',
        as_index=False
    )
    .agg({
        'Required Shifts': 'sum'
    })
)

# Machine Capacity
machine_summary['Available Shifts'] = (
    machine_summary['machine tonnage']
    .map({
        '100T': 312,
        '150T': 260
    })
)

# Machine Utilisation %
machine_summary['Utilisation %'] = (
    machine_summary['Required Shifts'] /
    machine_summary['Available Shifts']
) * 100

# Machine Status
machine_summary['Status'] = (
    machine_summary['Utilisation %']
    .apply(
        lambda x:
        'Underloaded' if x < 70
        else 'Normal' if x <= 100
        else 'Overloaded'
    )
)

# ---------------------------------------------------
# SHOW MACHINE SUMMARY
# ---------------------------------------------------

st.subheader("Machine-wise Capacity Summary")

def highlight_utilisation(val):

    if val > 100:
        return 'background-color: red'

    elif val > 85:
        return 'background-color: yellow'

    else:
        return 'background-color: lightgreen'

styled_machine_summary = (
    machine_summary
    .style
    .map(
        highlight_utilisation,
        subset=['Utilisation %']
    )
)

st.dataframe(styled_machine_summary)
# ---------------------------------------------------
# MACHINE UTILISATION CHART
# ---------------------------------------------------

machine_fig = px.bar(
    machine_summary,
    x='machine tonnage',
    y='Utilisation %',
    color='Status',
    title='Machine-wise Utilisation'
)

st.plotly_chart(machine_fig)
# ---------------------------------------------------
# RM CONSUMPTION SUMMARY
# ---------------------------------------------------

rm_summary = (
    master_df
    .groupby(
        'Raw Material Grade',
        as_index=False
    )
    .agg({
        'RM Required KG': 'sum'
    })
)

# ---------------------------------------------------
# RM CONSUMPTION CHART
# ---------------------------------------------------
st.markdown("## Raw Material Analytics")
rm_fig = px.bar(
    rm_summary,
    x='Raw Material Grade',
    y='RM Required KG',
    title='Raw Material Consumption'
)

st.plotly_chart(rm_fig)
# ---------------------------------------------------
# OVERLOAD ALERTS
# ---------------------------------------------------

st.subheader("Capacity Alerts")

for index, row in machine_summary.iterrows():

    if row['Utilisation %'] > 100:

        st.error(
            f"""
            {row['machine tonnage']} is OVERLOADED
            | Utilisation = {round(row['Utilisation %'], 2)}%
            """
        )

    elif row['Utilisation %'] > 85:

        st.warning(
            f"""
            {row['machine tonnage']} nearing full capacity
            | Utilisation = {round(row['Utilisation %'], 2)}%
            """
        )

    else:

        st.success(
            f"""
            {row['machine tonnage']} operating normally
            | Utilisation = {round(row['Utilisation %'], 2)}%
            """
        )

# ---------------------------------------------------
# DOWNLOAD BUTTON
# ---------------------------------------------------

with open(output_file, "rb") as file:

    st.download_button(
        label="Download Planning Report",
        data=file,
        file_name="Moulding_Planning_Output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )