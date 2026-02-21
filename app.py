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


# # -------------------------------
# # DATA LOADER (UNCHANGED LOGIC)
# # -------------------------------
# @st.cache_data
# def load_data(file):
#     if file.name.endswith(".csv"):
#         df = pd.read_csv(file)
#     else:
#         df = pd.read_excel(file)
#     return df.drop_duplicates()
#
#
# # -------------------------------
# # UPLOAD CARD
# # -------------------------------
# st.markdown('<div class="sneat-header">⚙️ Upload Dataset</div>', unsafe_allow_html=True)
#
# uploaded_file = st.file_uploader(
#     "Upload Dataset",
#     type=["csv", "xlsx"],
#     label_visibility="collapsed"
# )
#
# st.markdown('</div>', unsafe_allow_html=True)
#
# if not uploaded_file:
#     st.info("Please upload a file to begin analysis.")
#     st.stop()
# df = load_data(uploaded_file)


# -------------------------------
# DATA LOADER
# -------------------------------
@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    return df.drop_duplicates()


# -------------------------------
# INPUT SELECTION
# -------------------------------

input_method = st.radio(
    "Select Input Method",
    ["Upload File", "Paste Data"],
    horizontal=True
)

df = None


# -------------------------------
# CASE 1: UPLOAD FILE
# -------------------------------
if input_method == "Upload File":

    uploaded_file = st.file_uploader(
        "Upload Excel or CSV",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        df = load_data(uploaded_file)
    else:
        st.info("Please upload a file.")
        st.stop()


# -------------------------------
# CASE 2: PASTE DATA
# -------------------------------
elif input_method == "Paste Data":

    pasted_data = st.text_area(
        "Paste Excel/CSV Data Here (Ctrl + C / Ctrl + V)",
        height=200
    )

    if pasted_data.strip() != "":
        try:
            from io import StringIO

            df = pd.read_csv(StringIO(pasted_data), sep="\t")

            if df.shape[1] == 1:
                df = pd.read_csv(StringIO(pasted_data))

            df = df.drop_duplicates()
            st.success(
                f"✅ Dataset Loaded Successfully | "
                f"Rows: {len(df):,} | "
                f"Columns: {len(df.columns)} | "
                f"Memory: {round(df.memory_usage(deep=True).sum() / 1024 ** 2, 2)} MB"
            )

        except Exception:
            st.error("Invalid pasted data format.")
            st.stop()
    else:
        st.info("Please paste data.")
        st.stop()


# # -------------------------------
# # DATA PREVIEW
# # -------------------------------
# st.markdown("### 📌 Sample Data (First 5 Records)")
# st.dataframe(df.head(5), use_container_width=True)
#
# with st.expander("📂 View Full Dataset"):
#     st.dataframe(df, use_container_width=True)

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
# tab_data, tab_viz = st.tabs(["📑 Data Explorer", "📊 Analytics View"])

st.markdown("""
<style>

/* Make tabs look like modern pills */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

.stTabs [data-baseweb="tab"] {
    height: 45px;
    padding: 10px 22px;
    background-color: #f4f6f9;
    border-radius: 12px;
    font-weight: 600;
    color: #6c757d;
    transition: all 0.3s ease;
}

/* Active tab highlight */
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #696cff, #5a5ce6);
    color: white !important;
    box-shadow: 0 4px 12px rgba(105, 108, 255, 0.3);
}

/* Hover effect */
.stTabs [data-baseweb="tab"]:hover {
    background-color: #e4e6ff;
    color: #696cff;
}

</style>
""", unsafe_allow_html=True)

tab_data, tab_viz = st.tabs([
    "🗂 Data Explorer",
    "📈 Analytics Dashboard"
])


with tab_viz:

    chart_type = st.segmented_control(
        "Select Visualization Type",
        options=["Grouped Bar", "Line", "Pie", "Bar", "Stacked Bar", "Area", "Donut", "KPI Card"],
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
    # ------------------- Show KPI Card only -------------------
    if chart_type == "KPI Card":
        # Compute metrics
        total_val = melted["Val"].sum()
        avg_val = melted["Val"].mean()
        max_val = melted["Val"].max()

        # Modern KPI card HTML
        kpi_html = f"""
        <style>
        .kpi-container {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .kpi-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            flex: 1 1 200px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: transform 0.2s;
        }}
        .kpi-card:hover {{
            transform: translateY(-5px);
        }}
        .kpi-label {{
            font-size: 14px;
            opacity: 0.8;
        }}
        .kpi-value {{
            font-size: 28px;
            font-weight: bold;
            margin-top: 5px;
        }}
        .kpi-icon {{
            font-size: 24px;
            float: right;
            opacity: 0.7;
        }}
        </style>

        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-icon">💎</div>
                <div class="kpi-label">Total</div>
                <div class="kpi-value">{total_val:,.0f}</div>
            </div>
            <div class="kpi-card" style="background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);">
                <div class="kpi-icon">📊</div>
                <div class="kpi-label">Average</div>
                <div class="kpi-value">{avg_val:,.2f}</div>
            </div>
            <div class="kpi-card" style="background: linear-gradient(135deg, #fc5c7d 0%, #6a82fb 100%);">
                <div class="kpi-icon">🚀</div>
                <div class="kpi-label">Maximum</div>
                <div class="kpi-value">{max_val:,.0f}</div>
            </div>
        </div>
        """

        st.markdown(kpi_html, unsafe_allow_html=True)

    else:

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


with tab_data:
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
        background-color: #f0f1ff;
        color: #696cff;
        border-bottom: 2px solid #dcdfff;
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