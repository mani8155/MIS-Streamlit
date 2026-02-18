import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from io import BytesIO
import warnings

warnings.filterwarnings("ignore")

# Get query params
query_params = st.query_params

user_id = query_params.get("user_id")

if user_id:
    # st.success(f"User ID: {user_id}")
    pass
else:
    st.warning("user_id not found in URL")
    st.stop()

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Chart Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------
# MODERN UI CSS
# -------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

html, body { background-color: #f8fafc; }

.main .block-container {
    padding-top: 0rem;
    padding-bottom: 0.5rem;
    max-width: 1400px;
}


[data-testid="stSidebar"], footer, header, #MainMenu {
    display: none !important;
}

.section-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}

.section-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 0.3rem;
}

.section-sub {
    font-size: 0.95rem;
    color: #64748b;
    margin-bottom: 1rem;
}

.stPlotlyChart {
    border-radius: 12px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.08);
}

.generate-btn {
    position: sticky;
    bottom: 15px;
    z-index: 99;
}

hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg,#e2e8f0,#c7d2fe,#e2e8f0);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("""
<div style="text-align:center;margin-bottom:2rem">
<h1 style="font-size:2.7rem;font-weight:700;
background:linear-gradient(135deg,#4f46e5,#7c3aed);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent">
🚀 Pro Chart Analyzer
</h1>
<p style="color:#64748b;font-size:1.05rem">
Upload • Analyze • Visualize • Export
</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# -------------------------------------------------
# STEP 1: FILE UPLOAD
# -------------------------------------------------
st.markdown("""
<div class="section-card">
<div class="section-title">📤 Step 1: Upload Dataset</div>
<div class="section-sub">CSV / Excel supported • Auto cleaning enabled</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload File",
    type=["csv", "xlsx", "xls"],
    label_visibility="collapsed"
)

st.markdown("</div>", unsafe_allow_html=True)

if not uploaded_file:
    st.info("⬆️ Upload a dataset to continue")
    st.stop()

# -------------------------------------------------
# DATA PIPELINE (OPTIMIZED)
# -------------------------------------------------
@st.cache_data(show_spinner=False)
def load_and_clean(file):
    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    numeric_cols = []
    for col in df.columns:
        temp = pd.to_numeric(df[col], errors="coerce")
        if temp.notna().mean() > 0.5:
            df[col] = temp.fillna(temp.median())
            numeric_cols.append(col)

    cat_cols = df.columns.difference(numeric_cols)
    df[cat_cols] = df[cat_cols].fillna("Unknown").astype(str)

    return df.drop_duplicates()

with st.spinner("🔄 Processing dataset..."):
    df = load_and_clean(uploaded_file)

st.success(f"✅ Dataset Ready: {df.shape[0]:,} rows × {df.shape[1]} columns")

# -------------------------------------------------
# STEP 2: COLUMN SELECTION
# -------------------------------------------------
num_cols = df.select_dtypes(include=np.number).columns.tolist()
cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()

st.markdown("""
<div class="section-card">
<div class="section-title">🧠 Step 2: Select Columns</div>
<div class="section-sub">Choose numeric & categorical fields</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    selected_num = st.multiselect("📈 Numeric Columns", num_cols, num_cols[:3])
with col2:
    selected_cat = st.multiselect("🏷️ Category Columns", cat_cols, cat_cols[:2])

st.markdown("</div>", unsafe_allow_html=True)

if not (selected_num or selected_cat):
    st.warning("Select at least one column")
    st.stop()

# -------------------------------------------------
# CHART ENGINE
# -------------------------------------------------
def generate_charts(df, num_cols, cat_cols):
    charts = []
    df_viz = df[num_cols + cat_cols]

    if num_cols:
        melt_df = df_viz[num_cols].melt(var_name="Metric", value_name="Value")
        charts.append(px.histogram(melt_df, x="Value", color="Metric",
                                   nbins=30, opacity=0.7, title="📊 Distributions"))

        charts.append(px.box(df_viz[num_cols], title="📦 Spread & Outliers"))

        if len(num_cols) > 1:
            charts.append(px.imshow(
                df_viz[num_cols].corr(),
                color_continuous_scale="RdBu_r",
                title="🔗 Correlation Matrix"
            ))

    for col in cat_cols[:3]:
        vc = df_viz[col].value_counts().head(12)
        charts.append(px.bar(x=vc.index, y=vc.values, title=f"📊 {col} Counts"))
        charts.append(px.pie(values=vc.values, names=vc.index, title=f"🥧 {col} Proportions"))

    if num_cols:
        charts.append(px.scatter(
            df_viz.reset_index(),
            x="index", y=num_cols[0],
            title=f"📈 {num_cols[0]} Trend"
        ))

    return charts

# -------------------------------------------------
# GENERATE BUTTON (STICKY)
# -------------------------------------------------
st.markdown('<div class="generate-btn">', unsafe_allow_html=True)
generate = st.button("🚀 Generate Charts", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------
# CHARTS + SUMMARY
# -------------------------------------------------
if generate:
    st.markdown("""
    <div class="section-card">
    <div class="section-title">📊 Visual Analytics</div>
    <div class="section-sub">Interactive insights generated automatically</div>
    """, unsafe_allow_html=True)

    charts = generate_charts(df, selected_num, selected_cat)

    for fig in charts:
        fig.update_layout(height=360, margin=dict(t=60, b=30))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # SUMMARY
    st.markdown("""
    <div class="section-card">
    <div class="section-title">📈 Executive Summary</div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Columns", len(selected_num) + len(selected_cat))
    c3.metric("Numeric", len(selected_num))
    c4.metric("Category", len(selected_cat))

    st.markdown("</div>", unsafe_allow_html=True)

    # EXPORT
    st.markdown("""
    <div class="section-card">
    <div class="section-title">💾 Export Data</div>
    """, unsafe_allow_html=True)

    csv = df[selected_num + selected_cat].to_csv(index=False).encode()
    st.download_button("📥 Download CSV", csv, "chart_data.csv")

    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df[selected_num + selected_cat].to_excel(writer, index=False)

    st.download_button("📊 Download Excel", excel_buffer.getvalue(), "chart_data.xlsx")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# DATA PREVIEW
# -------------------------------------------------
with st.expander("👀 Preview Data (Top 100 rows)"):
    st.dataframe(df[selected_num + selected_cat].head(100), use_container_width=True)
