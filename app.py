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

# -------------------------------
# CONFIG
# -------------------------------
config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), 'custom_config.ini'))
DJANGO_APP_URL = config['DEFAULT']['DJANGO_APP_URL']

# -------------------------------
# FETCH DATA
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

#
# # -------------------------------
# # PIVOT CONFIGURATION
# # -------------------------------
# st.markdown('<div class="sneat-header">🧮 Pivot Configuration</div>', unsafe_allow_html=True)
#
# c1, c2, c3 = st.columns([1.2, 1.2, 2])
#
# # -------------------------------
# # ROWS
# # -------------------------------
# with c1:
#     st.markdown("**📌 Rows**")
#     row_cols = st.multiselect("Select Rows", cat_cols)
#
# # -------------------------------
# # COLUMNS
# # -------------------------------
# with c2:
#     st.markdown("**📊 Columns**")
#     col_cols = st.multiselect("Select Columns", cat_cols)
#
# # -------------------------------
# # METRICS (NEW UI)
# # -------------------------------
# with c3:
#     st.markdown("**📈 Metrics (Values & Aggregation)**")
#
#     value_config = []
#
#     metric_count = st.number_input(
#         "No. of Metrics",
#         min_value=1,
#         max_value=10,
#         value=1,
#         step=1
#     )
#
#     st.markdown("<hr>", unsafe_allow_html=True)
#
#     for i in range(metric_count):
#         m1, m2 = st.columns([2, 1])
#
#         with m1:
#             selected_col = st.selectbox(
#                 f"Metric {i+1}",
#                 num_cols,
#                 key=f"val_col_{i}"
#             )
#
#         with m2:
#             selected_agg = st.selectbox(
#                 "Agg",
#                 ["sum", "mean", "count", "max", "min"],
#                 key=f"val_agg_{i}"
#             )
#
#         value_config.append((selected_col, selected_agg))
#
# # -------------------------------
# # KEEP LAYOUT BALANCED
# # -------------------------------
# st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------
# PIVOT CONFIGURATION
# -------------------------------
st.markdown('<div class="sneat-header">🧮 Pivot Configuration</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1.2, 1.2, 2])



# -------------------------------
# COLUMNS
# -------------------------------
with c1:
    st.markdown("**📊 Columns**")
    col_cols = st.multiselect("Select Columns", cat_cols)

# -------------------------------
# ROWS
# -------------------------------
with c2:
    st.markdown("**📌 Rows**")
    row_cols = st.multiselect("Select Rows", cat_cols)

# -------------------------------
# METRICS (SAFE UI)
# -------------------------------
with c3:
    st.markdown("**📈 Metrics (Values & Aggregation)**")

    value_config = []

    metric_count = st.number_input(
        "No. of Metrics",
        min_value=1,
        max_value=10,
        value=1,
        step=1
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    used_combinations = set()

    for i in range(metric_count):
        m1, m2 = st.columns([2, 1])

        with m1:
            selected_col = st.selectbox(
                f"Metric {i+1}",
                ["-- Select Column --"] + num_cols,
                key=f"val_col_{i}"
            )

        with m2:
            selected_agg = st.selectbox(
                "Agg",
                ["-- Select --", "sum", "mean", "count", "max", "min"],
                key=f"val_agg_{i}"
            )

        # -------------------------------
        # VALIDATION
        # -------------------------------
        if selected_col != "-- Select Column --" and selected_agg != "-- Select --":

            combo = (selected_col, selected_agg)

            if combo in used_combinations:
                st.warning(f"⚠️ Duplicate metric: {selected_col} ({selected_agg})")
            else:
                used_combinations.add(combo)
                value_config.append(combo)



# -------------------------------
# FINAL VALIDATION BEFORE PIVOT
# -------------------------------
if len(value_config) == 0:
    st.info("❌ Please configure at least one valid metric")

elif not row_cols and not col_cols:
    st.info("❌ Select at least Rows or Columns")




# -------------------------------
# GLOBAL FILTERS
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

# -------------------------------
# VALIDATION
# -------------------------------
if not value_config:
    st.warning("Define 'Metrics' to visualize data.")
    st.stop()

# -------------------------------
# PIVOT
# -------------------------------
# -------------------------------
# SAFE PIVOT (ALL OPTIONAL)
# -------------------------------
pivot_df = pd.DataFrame()

try:
    # -------------------------------
    # CASE 1: NOTHING SELECTED → SHOW RAW DATA
    # -------------------------------
    if not row_cols and not col_cols and not value_config:
        pivot_df = df_filtered.copy()

    # -------------------------------
    # CASE 2: ONLY ROWS / COLUMNS (NO METRICS)
    # → COUNT MODE (Excel default behavior)
    # -------------------------------
    elif (row_cols or col_cols) and not value_config:
        pivot_df = pd.pivot_table(
            df_filtered,
            index=row_cols if row_cols else None,
            columns=col_cols if col_cols else None,
            aggfunc="size",   # 🔥 COUNT
            fill_value=0
        ).reset_index()

    # -------------------------------
    # CASE 3: METRICS PRESENT
    # -------------------------------
    else:
        agg_dict = {}
        for col, agg in value_config:
            agg_dict.setdefault(col, []).append(agg)

        pivot_df = pd.pivot_table(
            df_filtered,
            index=row_cols if row_cols else None,
            columns=col_cols if col_cols else None,
            values=list(agg_dict.keys()) if agg_dict else None,
            aggfunc=agg_dict if agg_dict else "size",
            fill_value=0
        )

        # -------------------------------
        # FIX MULTI-INDEX COLUMN ERROR
        # -------------------------------
        if isinstance(pivot_df.columns, pd.MultiIndex):
            pivot_df.columns = [
                " | ".join([str(i) for i in col if i])
                for col in pivot_df.columns.values
            ]

        pivot_df = pivot_df.reset_index()

except Exception as e:
    st.warning("⚠️ Pivot failed, showing raw data instead")
    pivot_df = df_filtered.copy()

# -------------------------------
# ✅ FIX: Arrow compatibility
# -------------------------------
for col in pivot_df.columns:
    pivot_df[col] = pivot_df[col].apply(
        lambda x: str(x) if isinstance(x, (list, dict)) else x
    )


# -------------------------------
# ✅ SAVE CONFIG + LINK
# -------------------------------
if st.button("📊 Show Chart"):
    link_placeholder = st.empty()

    pivot_config = {
        "rows": row_cols,
        "columns": col_cols if col_cols else [],
        "values": [
            {"column": col, "aggregation": agg}
            for col, agg in value_config
        ],
        "fill_value": 0,
        "filters": {}
    }

    for col in filter_cols:
        pivot_config["filters"][col] = df_filtered[col].dropna().unique().tolist()

    url = f"{DJANGO_APP_URL}update_pivot_config/{record_id}/"
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.put(
            url,
            headers=headers,
            data=json.dumps({"pivot_config": pivot_config})
        )

        if response.status_code == 200:
            redirect_url = f"{DJANGO_APP_URL}excel-upload/chart_view/{record_id}/"

            link_placeholder.markdown(f"""
                <a href="{redirect_url}" target="_blank"
                   style="display: inline-block;
                          padding: 12px 24px;
                          background-color: #4CAF50;
                          color: white;
                          text-decoration: none;
                          border-radius: 4px;
                          font-weight: bold;
                          margin-top: 10px;">
                    📊 Open Chart in New Tab
                </a>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Failed to save config")

    except Exception as e:
        st.error(f"❌ {str(e)}")


# -------------------------------
# DISPLAY TABLE (FINAL)
# -------------------------------
pivot_display = pivot_df.copy()
pivot_display.insert(0, "S.No", range(1, len(pivot_display) + 1))

numeric_cols = pivot_display.select_dtypes(include=np.number).columns.tolist()
if "S.No" in numeric_cols:
    numeric_cols.remove("S.No")

# -------------------------------
# GRAND TOTAL ROW
# -------------------------------
grand_total = pivot_display[numeric_cols].sum().to_dict()
grand_total["S.No"] = ""

for col in pivot_display.columns:
    if col not in grand_total:
        grand_total[col] = "Grand Total"

grand_total_df = pd.DataFrame([grand_total])
grand_total_df = grand_total_df.reindex(columns=pivot_display.columns)

pivot_display = pd.concat(
    [pivot_display, grand_total_df],
    ignore_index=True
)

# -------------------------------
# HTML TABLE (MULTI HEADER)
# -------------------------------
table_html = pivot_display.to_html(
    index=False,
    classes="premium-table",
    border=0
)



st.markdown("""
<style>
.table-card {
    background: #fff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(67, 89, 113, 0.1);
    border: 1px solid #d9dee3;
}

.table-responsive {
    width: 100%;
    max-height: 450px;
    overflow-y: auto;
    overflow-x: auto;
}

.table-responsive::-webkit-scrollbar {
    height: 8px;
    width: 8px;
}
.table-responsive::-webkit-scrollbar-thumb {
    background: #d4d8dd;
    border-radius: 10px;
}

.premium-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    min-width: 900px;
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