import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import warnings
import requests
from io import BytesIO
import configparser
import os
import json
import time

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Premium Analytics",
    page_icon="💎",
    layout="wide"
)

# -------------------------------
# SNEAT STYLE CSS
# -------------------------------
st.markdown("""
<style>
.block-container { padding: 1.5rem 2rem !important; }
header, footer { visibility: hidden !important; }
html, body { background-color: #f8fafc; }

span[data-baseweb="tag"] {
    background-color: #696cff !important;
    color: white !important;
    border-radius: 4px !important;
}

.sneat-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid #d9dee3;
    box-shadow: 0 4px 12px 0 rgba(67, 89, 113, 0.1);
}

.sneat-header {
    color: #566a7f;
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 15px;
}



</style>
""", unsafe_allow_html=True)

# DJANGO_APP_URL = "http://localhost:8312/"
# DJANGO_APP_URL = "https://allydax.com/"

config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), 'custom_config.ini'))
# Create your views here.
DJANGO_APP_URL = config['DEFAULT']['DJANGO_APP_URL']

# -------------------------------
# FETCH DATA (CACHED)
# -------------------------------
@st.cache_data(show_spinner=False)
def fetch_excel_data(record_id):
    try:
        url = f"{DJANGO_APP_URL}download_excel_api/{record_id}/"
        response = requests.get(url, timeout=10)


        if response.status_code != 200:
            return None, "API Error"

        excel_data = BytesIO(response.content)
        df = pd.read_excel(excel_data)

        if df.empty:
            return None, "Empty file"

        return df, None

    except requests.exceptions.Timeout:
        return None, "Request Timeout"
    except Exception as e:
        return None, str(e)


# -------------------------------
# GET QUERY PARAM
# -------------------------------
record_id = st.query_params.get("record_id")
print(record_id)

# st.write("Received ID:", record_id)
# st.write("Received ID:", record_id)

if not record_id:
    st.warning("❗ No ID provided in URL")
    st.stop()

# -------------------------------
# LOAD DATA
# -------------------------------
with st.spinner("Loading Excel data..."):
    df, error = fetch_excel_data(record_id)

if error:
    st.error(f"❌ {error}")
    st.stop()

# -------------------------------
# COLUMN DETECTION
# -------------------------------
num_cols = df.select_dtypes(include=np.number).columns.tolist()
cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()





# -------------------------------
# PIVOT CONFIGURATION CARD
# -------------------------------
st.markdown('<div class="sneat-header">🧮 Pivot Configuration</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    row_cols = st.multiselect("Rows (Categories)", cat_cols)

with c2:
    col_cols = st.multiselect("Columns (Series)", cat_cols)

with c3:
    val_cols = st.multiselect("Metrics (Values)", num_cols)

with c4:
    agg_func = st.selectbox("Aggregation", ["sum", "mean", "count", "max", "min"])


st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------
# GLOBAL FILTERS CARD
# -------------------------------
st.markdown('<div class="sneat-header">🔍 Global Filters</div>', unsafe_allow_html=True)

filter_cols = st.multiselect("Filter by", cat_cols)

df_filtered = df.copy()

if filter_cols:
    filter_columns = st.columns(len(filter_cols))
    for i, col in enumerate(filter_cols):
        with filter_columns[i]:
            options = df[col].dropna().unique().tolist()
            selected = st.multiselect(f"{col}", options)
            if selected:
                df_filtered = df_filtered[df_filtered[col].isin(selected)]

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# ================= YOUR CODE BELOW (UNCHANGED) ===========
# =========================================================


# if not row_cols or not val_cols:
#     st.warning("Define 'Rows' and 'Metrics' to visualize data.")
#     st.stop()

if not val_cols:
    st.warning("Define 'Metrics' to visualize data.")
    st.stop()


# 2. DATA PROCESSING
try:
    # pivot_df = pd.pivot_table(
    #     df_filtered,
    #     index=row_cols,
    #     columns=col_cols if col_cols else None,
    #     values=val_cols,
    #     aggfunc=agg_func,
    #     fill_value=0
    # )

    pivot_df = pd.pivot_table(
        df_filtered,
        index=row_cols if row_cols else None,
        columns=col_cols if col_cols else None,
        values=val_cols,
        aggfunc=agg_func,
        fill_value=0
    )

    if isinstance(pivot_df.columns, pd.MultiIndex):
        pivot_df.columns = ['_'.join(map(str, c)) for c in pivot_df.columns]

    # pivot_df = pivot_df.reset_index()

    pivot_df = pivot_df.reset_index()

    # ✅ Handle case when no rows selected
    if not row_cols:
        pivot_df = pivot_df.reset_index(drop=True)

except Exception as e:
    st.error(f"Error building pivot: {e}")
    st.stop()


if st.button("📊 Show Chart"):
    # Create placeholder for status messages
    status_placeholder = st.empty()
    link_placeholder = st.empty()

    # -------------------------------
    # Build pivot config including filters
    # -------------------------------
    pivot_config = {
        "rows": row_cols,  # selected row fields
        "columns": col_cols if col_cols else [],  # selected column fields
        "values": val_cols,  # selected value fields
        "aggfunc": agg_func,  # aggregation function
        "fill_value": 0,  # missing cells replacement
        "filters": {}  # global filters applied
    }

    # Add selected filter values
    for col in filter_cols:
        selected = df_filtered[col].unique().tolist()
        pivot_config["filters"][col] = selected

    # -------------------------------
    # Send pivot config to Django API
    # -------------------------------
    url = f"{DJANGO_APP_URL}update_pivot_config/{record_id}/"
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({"pivot_config": pivot_config})

    success = False
    try:
        response = requests.put(url, headers=headers, data=payload)
        if response.status_code == 200:
            success = True
        else:
            status_placeholder.error(f"❌ Failed to save pivot config: {response.status_code}")
    except Exception as e:
        status_placeholder.error(f"❌ Error: {e}")

    # If API call was successful, show clickable link
    if success:
        redirect_url = f"{DJANGO_APP_URL}excel-upload/chart_view/{record_id}/"

        # Show clickable link to open in new tab
        link_placeholder.markdown(f"""
            <a href="{redirect_url}" target="_blank" style="display: inline-block; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; margin-top: 10px; cursor: pointer;">
                📊 Open Chart in New Tab
            </a>
        """, unsafe_allow_html=True)

# ✅ CLEAN COLUMN NAMES
if isinstance(pivot_df.columns, pd.MultiIndex):
    pivot_df.columns = [
        col[1] if col[1] else col[0]
        for col in pivot_df.columns
    ]
else:
    pivot_df.columns = [
        col.split("_")[-1] if "_" in str(col) else col
        for col in pivot_df.columns
    ]

pivot_display = pivot_df.copy()
pivot_display.insert(0, "S.No", range(1, len(pivot_display) + 1))

# Fetch numeric columns, but EXCLUDE 'S.No'
numeric_cols = pivot_display.select_dtypes(include=np.number).columns.tolist()
if "S.No" in numeric_cols:
    numeric_cols.remove("S.No")

grand_total = pivot_display[numeric_cols].sum().to_dict()
grand_total["S.No"] = ""

for col in pivot_display.columns:
    if col not in grand_total:
        grand_total[col] = "Grand Total"

pivot_display = pd.concat(
    [pivot_display, pd.DataFrame([grand_total])],
    ignore_index=True
)

# -------------------------------
# GRAND TOTAL COLUMN
# -------------------------------
# 'S.No' is safely ignored here now
pivot_display["Grand Total"] = pivot_display[numeric_cols].sum(axis=1)

table_html = pivot_display.to_html(index=False, classes="premium-table", border=0)

st.markdown("""
<style>
.table-card {
    background: #fff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(67, 89, 113, 0.1);
    border: 1px solid #d9dee3;
}

/* Scroll container like Sneat */
.table-responsive {
    width: 100%;
    max-height: 450px;
    overflow-y: auto;
    overflow-x: auto;
}

/* Custom scrollbar (Sneat feel) */
.table-responsive::-webkit-scrollbar {
    height: 8px;
    width: 8px;
}
.table-responsive::-webkit-scrollbar-thumb {
    background: #d4d8dd;
    border-radius: 10px;
}
.table-responsive::-webkit-scrollbar-thumb:hover {
    background: #bfc5cc;
}

/* Table styling */
.premium-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    min-width: 900px; /* force horizontal scroll */
}

.premium-table thead th {
    position: sticky;
    top: 0;
    background: #f5f6ff;
    color: #696cff;
    font-size: 12px;
    text-transform: uppercase;
    z-index: 2;
    padding: 12px;
}

.premium-table td {
    padding: 10px 12px;
    border-bottom: 1px solid #eceef1;
    color: #566a7f;
}

.premium-table tbody tr:hover {
    background: #f9f9ff;
}

/* Optional: last row highlight */
.premium-table tbody tr:last-child {
    font-weight: 600;
    background: #f8f9ff;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="table-card">
    <div class="table-responsive">
        {table_html}
    </div>
</div>
""", unsafe_allow_html=True)


