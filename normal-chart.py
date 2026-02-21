import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import warnings

# --- SETUP & THEMING ---
warnings.filterwarnings("ignore")
st.set_page_config(
    page_title="Premium Analytics",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS for Cards and Headers
st.markdown("""
<style>
/* Hides the Deploy button */
        .stAppDeployButton {
            display: none !important;
        }

        /* Hides the Hamburger Menu (three dots) */
        #MainMenu {
            visibility: hidden;
        }

        /* Hides the Footer (Made with Streamlit) */
        footer {
            visibility: hidden;
        }

    .block-container { padding-top: 1.5rem !important; }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #696cff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .chart-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e0e2e6;
    }
</style>
""", unsafe_allow_html=True)


# --- HELPER FUNCTIONS ---
@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    return df.drop_duplicates()


# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.title("💎 Config")
    uploaded_file = st.file_uploader("Upload Data Source", type=["csv", "xlsx"])

    if not uploaded_file:
        st.info("Please upload a file to begin.")
        st.stop()

    df = load_data(uploaded_file)
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()

    st.subheader("🧮 Pivot Logic")
    row_cols = st.multiselect("Rows (Categories)", cat_cols, help="Fields for the X-axis")
    col_cols = st.multiselect("Columns (Series)", cat_cols, help="Sub-segments for grouping")
    val_cols = st.multiselect("Metrics (Values)", num_cols)
    agg_func = st.selectbox("Aggregation", ["sum", "mean", "count", "max", "min"], index=0)

    st.subheader("🔍 Global Filters")
    filter_cols = st.multiselect("Filter by", cat_cols)
    df_filtered = df.copy()
    for col in filter_cols:
        options = df[col].dropna().unique().tolist()
        selected = st.multiselect(f"Select {col}", options)
        if selected:
            df_filtered = df_filtered[df_filtered[col].isin(selected)]

# --- MAIN CONTENT ---
st.title("Business Intelligence Insights")
st.markdown('<a href="#" target="_blank" class="new-tab-button"><span>↗️</span> Open in New Tab</a>',
            unsafe_allow_html=True)

# Validation check
if not row_cols or not val_cols:
    st.warning("👈 Define 'Rows' and 'Metrics' in the sidebar to visualize data.")
    st.stop()

# 1. KPI CARDS SECTION
st.subheader("🎯 Key Performance Indicators")
kpi_cols = st.columns(len(val_cols) + 1)

# Total Records KPI
kpi_cols[0].metric("Total Rows", f"{len(df_filtered):,}")

# Dynamic KPIs for selected metrics
for i, v_col in enumerate(val_cols):
    res = getattr(df_filtered[v_col], agg_func)()
    label = f"{agg_func.upper()} {v_col}"
    if res >= 1_000_000:
        val_str = f"{res / 1_000_000:.1f}M"
    elif res >= 1_000:
        val_str = f"{res / 1_000:.1f}K"
    else:
        val_str = f"{res:,.2f}"
    kpi_cols[i + 1].metric(label, val_str)

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
    # Flatten multi-level columns if user chose "Columns"
    if isinstance(pivot_df.columns, pd.MultiIndex):
        pivot_df.columns = ['_'.join(map(str, c)) for c in pivot_df.columns]

    pivot_df = pivot_df.reset_index()
except Exception as e:
    st.error(f"Error building pivot: {e}")
    st.stop()

# 3. TABS FOR VISUALIZATION
tab_viz, tab_data = st.tabs(["📑 Data Explorer", "📊 Analytics View"])

with tab_viz:
    # Modern Choice Selection
    chart_type = st.segmented_control(
        "Select Visualization Type",
        options=["Grouped Bar", "Line", "Pie", "Bar", "Stacked Bar", "Area", "Donut"],
        default="Grouped Bar"
    )

    # Prepare plotting data
    # We use the first row column as the main X-axis
    main_x = row_cols[0]
    plot_cols = [c for c in pivot_df.columns if c not in row_cols]

    # Melt data for Plotly Long Format
    melted = pivot_df.melt(id_vars=row_cols, value_vars=plot_cols, var_name="Metric", value_name="Val")

    # st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    #
    # fig = None
    # if chart_type == "Bar":
    #     fig = px.bar(melted, x=main_x, y="Val", color="Metric", template="plotly_white")
    #
    # elif chart_type == "Stacked Bar":
    #     fig = px.bar(melted, x=main_x, y="Val", color="Metric", barmode="relative")
    #
    # elif chart_type == "Grouped Bar":
    #     fig = px.bar(melted, x=main_x, y="Val", color="Metric", barmode="group")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)

    fig = None

    if chart_type == "Bar":
        # SIMPLE BAR: Sum all metrics to show one total bar per category
        simple_bar_data = melted.groupby(main_x)["Val"].sum().reset_index()
        fig = px.bar(
            simple_bar_data,
            x=main_x,
            y="Val",
            template="plotly_white",
            color_discrete_sequence=['#696cff']  # Premium solid color
        )
        fig.update_layout(showlegend=False)

    elif chart_type == "Stacked Bar":
        # STACKED: Metrics placed on top of each other (Default px.bar behavior)
        fig = px.bar(melted, x=main_x, y="Val", color="Metric", barmode="relative")

    elif chart_type == "Grouped Bar":
        # GROUPED: Metrics placed side-by-side
        fig = px.bar(melted, x=main_x, y="Val", color="Metric", barmode="group")

    elif chart_type == "Line":
        fig = px.line(melted, x=main_x, y="Val", color="Metric", markers=True)

    elif chart_type == "Area":
        fig = px.area(melted, x=main_x, y="Val", color="Metric")

    elif chart_type in ["Pie", "Donut"]:
        # Group metrics for total pie view
        pie_data = melted.groupby(main_x)["Val"].sum().reset_index()
        is_donut = 0.4 if chart_type == "Donut" else 0
        fig = px.pie(pie_data, names=main_x, values="Val", hole=is_donut)

    if fig:
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

with tab_data:
    st.subheader("Pivot Table Result")
    st.dataframe(pivot_df, use_container_width=True)

    # Download Button
    csv_data = pivot_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download This Table", data=csv_data, file_name="analytics_export.csv", mime="text/csv")
