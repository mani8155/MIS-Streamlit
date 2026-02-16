import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stToolbar"], footer, header,
#MainMenu, [data-testid="collapsedControl"] {
    display: none !important;
}
.block-container {
    padding-top: 0.2rem;
    padding-left: 1.2rem;
    padding-right: 1.2rem;
    max-width: 100%;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# GET URL PARAMETERS
# -------------------------------------------------
params = st.query_params
id_value = params.get("id")
req_value = params.get("req")

if not id_value:
    st.warning("ID missing")
    st.stop()

# -------------------------------------------------
# UI SELECTOR FOR VIEW TYPE
# -------------------------------------------------
ui_type = st.radio(
    "Select View",
    ["Table", "Pie", "Line", "Bar", "Area", "JSON"],
    horizontal=True
).lower()

# -------------------------------------------------
# API CALL
# -------------------------------------------------
if req_value == 'excel':
    url = "https://api.nanoxlabs.com/getapi/dms_hmsi_07_tally_stock/all"
else:
    url = "https://api.nanoxlabs.com/getapi/dms_hmsi_07_tally_stock"

response = requests.get(url, params={"id": id_value})
data = response.json()

df = pd.DataFrame(data)
if df.empty:
    st.warning("No data available")
    st.stop()

# -------------------------------------------------
# UNIVERSAL MELT FOR PLOTS
# -------------------------------------------------
x_col = df.columns[0]

melt_df = df.melt(
    id_vars=[x_col],
    var_name="column",
    value_name="value"
)

# -------------------------------------------------
# RENDER UI BASED ON USER SELECTION
# -------------------------------------------------
if ui_type == "line":
    fig = px.line(melt_df, x=x_col, y="value", color="column")
    st.plotly_chart(fig, use_container_width=True)

elif ui_type == "area":
    fig = px.area(melt_df, x=x_col, y="value", color="column")
    st.plotly_chart(fig, use_container_width=True)

elif ui_type == "bar":
    fig = px.bar(melt_df, x=x_col, y="value", color="column", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

elif ui_type == "pie":
    pie_df = melt_df.groupby("column", as_index=False)["value"].count()
    fig = px.pie(pie_df, names="column", values="value")
    st.plotly_chart(fig, use_container_width=True)

elif ui_type == "json":
    st.json(data)

else:  # Table view
    st.dataframe(df, use_container_width=True)
