import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from io import BytesIO

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Smart Chart Generator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# CLEAN UI
# -------------------------------------------------
st.markdown("""
<style>
[data-testid="stSidebar"], footer, header, #MainMenu {
    display: none !important;
}
.block-container {
    max-width: 1200px;
    padding-top: 1rem;
}
.center { text-align:center; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# TITLE
# -------------------------------------------------
st.markdown("<h2 class='center'>🚀 Smart Excel Chart Generator</h2>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# -------------------------------------------------
# STEP 1 – FILE UPLOAD
# -------------------------------------------------
st.markdown("### 📤 Step 1: Upload Excel File")

uploaded_file = st.file_uploader(
    "Choose your Excel file",
    type=["xlsx", "xls"],
    label_visibility="collapsed",
    help="Upload .xlsx or .xls file to analyze"
)

if not uploaded_file:
    st.info("👆 Please upload an Excel file to get started")
    st.stop()

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
st.markdown("### ⏳ Loading data...")
df = pd.read_excel(uploaded_file)
st.success(f"✅ Data loaded: {df.shape[0]} rows × {df.shape[1]} columns")

# -------------------------------------------------
# STEP 2 – MULTI-COLUMN SELECTION (SAME UI)
# -------------------------------------------------
st.markdown("### 🧩 Step 2: Choose Columns for Analysis")

columns = df.columns.tolist()
selected_cols = st.multiselect(
    "Select columns to visualize:",
    columns,
    default=columns[:3] if len(columns) >= 3 else columns,
    help="Multi-select - app auto-generates BIG DATA charts!"
)

if not selected_cols:
    st.warning("Please select at least 1 column")
    st.stop()

col_data = df[selected_cols].dropna()
st.info(f"Selected **{len(selected_cols)}** columns - {len(col_data)} valid rows")

# -------------------------------------------------
# STEP 3 – BEST 5 BIG DATA CHARTS
# -------------------------------------------------
st.markdown("### 📊 Step 3: Top 5 Smart Charts")

if st.button("🎨 Generate Best Charts", use_container_width=True):

    df_clean = df[selected_cols].dropna()

    col1, col2, col3 = st.columns(3)

    # Chart 1: Multi-Histogram (Big Data Distribution)
    with col1:
        st.markdown("**1. Multi-Distribution**")
        melt_df = df_clean.melt(var_name='Column', value_name='Value')
        fig1 = px.histogram(
            melt_df, x='Value', y='Column', color='Column',
            nbins=50, histfunc='count',
            title="All Columns Distribution",
            template="plotly_white",
            height=320
        )
        fig1.update_layout(margin=dict(t=50))
        st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Multi-Box Plot (Outliers Detection)
    with col2:
        st.markdown("**2. Big Data Boxplots**")
        melt_df_box = df_clean.melt(var_name='Column', value_name='Value')
        fig2 = px.box(
            melt_df_box, x='Column', y='Value', color='Column',
            title="Outliers & Quartiles",
            template="plotly_white",
            height=320
        )
        fig2.update_layout(margin=dict(t=50))
        st.plotly_chart(fig2, use_container_width=True)

    # Chart 3: Heatmap (Multi-Column Correlations)
    with col3:
        st.markdown("**3. Correlation Matrix**")
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            corr_matrix = df_clean[numeric_cols].corr()
            fig3 = px.imshow(
                corr_matrix,
                title="Big Data Correlations",
                color_continuous_scale="RdBu_r",
                aspect="auto",
                template="plotly_white",
                height=320
            )
        else:
            # Fallback: Top value counts
            top_vc = df_clean.iloc[:, 0].value_counts().head(15)
            fig3 = px.bar(x=top_vc.index, y=top_vc.values,
                          title="Top Categories", template="plotly_white", height=320)
        fig3.update_layout(margin=dict(t=50))
        st.plotly_chart(fig3, use_container_width=True)

    col4, col5 = st.columns(2)

    # Chart 4: Violin (High-Density Distribution)
    with col4:
        st.markdown("**4. Density Violin**")
        melt_df_violin = df_clean.melt(var_name='Column', value_name='Value')
        fig4 = px.violin(
            melt_df_violin, y='Value', x='Column', color='Column',
            box=True, points=False,
            title="Data Density",
            template="plotly_white",
            height=320
        )
        fig4.update_layout(margin=dict(t=50))
        st.plotly_chart(fig4, use_container_width=True)

    # Chart 5: FIXED Multi-Dimensional (No diagonal param)
    with col5:
        st.markdown("**5. Multi-Dimensional**")
        numeric_cols_clean = df_clean.select_dtypes(include=[np.number])
        if len(numeric_cols_clean.columns) >= 2:
            # FIXED: Use px.scatter_matrix without diagonal param
            fig5 = px.scatter_matrix(
                numeric_cols_clean,
                title="Big Data Relationships",
                template="plotly_white",
                height=320
            )
        else:
            # Trendline for single numeric or bar for categorical
            if len(numeric_cols_clean.columns) == 1:
                num_col = numeric_cols_clean.columns[0]
                fig5 = px.scatter(df_clean.reset_index(),
                                  x='index', y=num_col, trendline="ols",
                                  title=f"Trend: {num_col}",
                                  template="plotly_white", height=320)
            else:
                cat_col = selected_cols[0]
                vc = df[cat_col].value_counts().head(20)
                fig5 = px.treemap(names=vc.index, parents=[''] * len(vc),
                                  values=vc.values, title=f"Treemap: {cat_col}",
                                  template="plotly_white", height=320)
        fig5.update_layout(margin=dict(t=50))
        st.plotly_chart(fig5, use_container_width=True)

    # BIG DATA SUMMARY
    st.markdown("### 📈 Big Data Insights")
    col_summary1, col_summary2, col_summary3 = st.columns(3)

    with col_summary1:
        st.metric("Analyzed Rows", f"{len(df_clean):,}")
        if len(selected_cols) > 0:
            st.metric("Columns", len(selected_cols))

    with col_summary2:
        num_cols = len(df_clean.select_dtypes(include=[np.number]).columns)
        cat_cols = len(df_clean.select_dtypes(exclude=[np.number]).columns)
        st.metric("Numeric", num_cols)
        st.metric("Categorical", cat_cols)

    with col_summary3:
        total_unique = sum(df_clean[col].nunique() for col in selected_cols)
        st.metric("Total Unique", f"{total_unique:,}")
        st.metric("Memory (MB)", f"{df_clean.memory_usage(deep=True).sum() / 1e6:.1f}")

    # Raw data preview
    with st.expander("👀 View Clean Data"):
        st.dataframe(df_clean.head(100), use_container_width=True)

    # OPTIMIZED EXPORTS
    st.markdown("### 💾 Big Data Export")
    csv_buffer = BytesIO()
    df_clean.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    st.download_button(
        "📥 Download Clean CSV",
        csv_buffer,
        file_name=f"bigdata_analysis_{'_'.join(selected_cols)}.csv",
        mime="text/csv",
        use_container_width=True
    )
