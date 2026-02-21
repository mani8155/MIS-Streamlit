import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import warnings

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
# DATA LOADER (UNCHANGED LOGIC)
# -------------------------------
@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    return df.drop_duplicates()


# -------------------------------
# UPLOAD CARD
# -------------------------------
st.markdown('<div class="sneat-header">⚙️ Upload Dataset</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Dataset",
    type=["csv", "xlsx"],
    label_visibility="collapsed"
)

st.markdown('</div>', unsafe_allow_html=True)

if not uploaded_file:
    st.info("Please upload a file to begin analysis.")
    st.stop()

df = load_data(uploaded_file)
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

if not row_cols or not val_cols:
    st.warning("Define 'Rows' and 'Metrics' to visualize data.")
    st.stop()


# 2. DATA PROCESSING
try:
    pivot_df = pd.pivot_table(
        df_filtered,
        index=row_cols,
        columns=col_cols if col_cols else None,
        values=val_cols,
        aggfunc=agg_func,
        fill_value=0
    )

    if isinstance(pivot_df.columns, pd.MultiIndex):
        pivot_df.columns = ['_'.join(map(str, c)) for c in pivot_df.columns]

    pivot_df = pivot_df.reset_index()

except Exception as e:
    st.error(f"Error building pivot: {e}")
    st.stop()

# 3. TABS FOR VISUALIZATION
tab_data, tab_viz = st.tabs(["📑 Data Explorer", "📊 Analytics View"])

with tab_viz:

    chart_type = st.segmented_control(
        "Select Visualization Type",
        options=["Grouped Bar", "Line", "Pie", "Bar", "Stacked Bar", "Area", "Donut"],
        default="Grouped Bar"
    )

    main_x = row_cols[0]
    plot_cols = [c for c in pivot_df.columns if c not in row_cols]

    melted = pivot_df.melt(
        id_vars=row_cols,
        value_vars=plot_cols,
        var_name="Metric",
        value_name="Val"
    )

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)

    fig = None

    if chart_type == "Bar":
        simple_bar_data = melted.groupby(main_x)["Val"].sum().reset_index()
        fig = px.bar(
            simple_bar_data,
            x=main_x,
            y="Val",
            template="plotly_white",
            color_discrete_sequence=['#696cff']
        )
        fig.update_layout(showlegend=False)

    elif chart_type == "Stacked Bar":
        fig = px.bar(melted, x=main_x, y="Val", color="Metric", barmode="relative")

    elif chart_type == "Grouped Bar":
        fig = px.bar(melted, x=main_x, y="Val", color="Metric", barmode="group")

    elif chart_type == "Line":
        fig = px.line(melted, x=main_x, y="Val", color="Metric", markers=True)

    elif chart_type == "Area":
        fig = px.area(melted, x=main_x, y="Val", color="Metric")

    elif chart_type in ["Pie", "Donut"]:
        pie_data = melted.groupby(main_x)["Val"].sum().reset_index()
        is_donut = 0.4 if chart_type == "Donut" else 0
        fig = px.pie(pie_data, names=main_x, values="Val", hole=is_donut)

    if fig:
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# with tab_data:
#     st.subheader("Pivot Table Result")
#
#     pivot_display = pivot_df.copy()
#     pivot_display.insert(0, "S.No", range(1, len(pivot_display) + 1))
#
#     numeric_cols = pivot_display.select_dtypes(include=np.number).columns.tolist()
#
#     grand_total = pivot_display[numeric_cols].sum().to_dict()
#     grand_total["S.No"] = ""
#
#     for col in pivot_display.columns:
#         if col not in grand_total:
#             grand_total[col] = "Grand Total"
#
#     pivot_display = pd.concat(
#         [pivot_display, pd.DataFrame([grand_total])],
#         ignore_index=True
#     )
#
#     st.dataframe(pivot_display, use_container_width=True)
#
#     csv_data = pivot_display.to_csv(index=False).encode('utf-8')
#
#     st.download_button(
#         "📥 Download This Table",
#         data=csv_data,
#         file_name="analytics_export.csv",
#         mime="text/csv"
#     )


with tab_data:

    pivot_display = pivot_df.copy()
    pivot_display.insert(0, "S.No", range(1, len(pivot_display) + 1))

    numeric_cols = pivot_display.select_dtypes(include=np.number).columns.tolist()

    grand_total = pivot_display[numeric_cols].sum().to_dict()
    grand_total["S.No"] = ""

    for col in pivot_display.columns:
        if col not in grand_total:
            grand_total[col] = "Grand Total"

    pivot_display = pd.concat(
        [pivot_display, pd.DataFrame([grand_total])],
        ignore_index=True
    )

    table_html = pivot_display.to_html(index=False, classes="premium-table", border=0)

    st.markdown("""
    <style>
    .table-card {
        background: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(67, 89, 113, 0.1);
        border: 1px solid #d9dee3;
        overflow-x: auto;
    }

    .premium-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }

    .premium-table thead {
        background-color: #696cff;
        color: white;
    }

    .premium-table th {
        padding: 12px 15px;
        text-transform: uppercase;
        font-size: 12px;
    }

    .premium-table td {
        padding: 10px 15px;
        border-bottom: 1px solid #f0f0f0;
        color: #566a7f;
    }

    .premium-table tbody tr:hover {
        background-color: #f5f5f9;
    }

    .premium-table tbody tr:last-child {
        font-weight: 700;
        background-color: #f8f9ff;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="table-card">
        {table_html}
    </div>
    """, unsafe_allow_html=True)