import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Data Transformation",
    layout="wide"
)

st.title("Production Data Transformation")

# ---------------------------------------------------
# READ EXCEL FILE
# ---------------------------------------------------

excel_file = pd.ExcelFile(
    "DAILY PRODUCTION CHART (1).xlsx"
)

sheet_names = excel_file.sheet_names

# ---------------------------------------------------
# SHOW SHEETS
# ---------------------------------------------------

st.subheader("Available Sheets")

st.write(sheet_names)

# ---------------------------------------------------
# SELECT SHEET
# ---------------------------------------------------

selected_sheet = st.selectbox(
    "Select Month Sheet",
    sheet_names
)

# ---------------------------------------------------
# READ SHEET
# ---------------------------------------------------

df = pd.read_excel(
    excel_file,
    sheet_name=selected_sheet,
    header=None
)

# ---------------------------------------------------
# SHOW RAW DATA
# ---------------------------------------------------

st.subheader("Raw Sheet Data")

st.dataframe(df)

# ---------------------------------------------------
# EXTRACT DATE ROW
# ---------------------------------------------------

date_row = df.iloc[3]

st.subheader("Date Row")

st.write(date_row)

# ---------------------------------------------------
# EXTRACT ITEM DATA
# ---------------------------------------------------

item_data = df.iloc[5:]

st.subheader("Production Data")

st.dataframe(item_data)

# ---------------------------------------------------
# TOTAL RECORDS
# ---------------------------------------------------

st.success(
    f"Rows Extracted: {len(item_data)}"
)