
import os
from io import BytesIO
import pandas as pd
import requests
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="TFC KPI Dashboard", layout="wide")

# ------------------ Helpers ------------------ #
@st.cache_data(show_spinner="📊 Loading Excel ...")
def load_excel(source: str) -> dict:
    """Return dict of DataFrames keyed by sheet name."""
    if source.startswith(("http://", "https://")):
        try:
            r = requests.get(source, timeout=15)
            r.raise_for_status()
            return pd.read_excel(BytesIO(r.content), sheet_name=None)
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Could not download file. Details: {e}")
            st.stop()
    else:
        if not os.path.exists(source):
            st.error(f"❌ File not found: {source}")
            st.stop()
        return pd.read_excel(source, sheet_name=None)

def _extract_financial(fin_raw: pd.DataFrame) -> pd.DataFrame:
    """Tidy the messy 'finance report' sheet into Round‑Metric columns."""
    # Work on a copy to avoid SettingWithCopy warnings
    df0 = fin_raw.copy()
    # first numeric row (index 1) holds column labels 0..6
    col_labels = ['Metric'] + df0.iloc[1,1:].tolist()
    df = df0.iloc[2:].reset_index(drop=True)
    df.columns = col_labels
    # mapping aggregated metrics to simple names
    regex_map = {
        'ROI': r'^ROI$',
        'Realized Revenues': r'^Realized revenue$',
        'COGS': r'Gross margin - Cost of goods sold$',
        'Indirect Cost': r'Operating profit - Indirect cost$'
    }
    frames = []
    for nice, regex in regex_map.items():
        row = df[df['Metric'].str.match(regex, case=False, na=False)]
        if not row.empty:
            ser = row.iloc[0].drop('Metric').rename(nice).reset_index()
            ser.columns = ['Round', nice]
            frames.append(ser)
    if not frames:
        st.error("❌ Could not locate core financial KPIs in finance sheet.")
        st.stop()
    fin_df = frames[0]
    for fr in frames[1:]:
        fin_df = fin_df.merge(fr, on='Round', how='outer')
    # ensure numeric and int round
    fin_df['Round'] = fin_df['Round'].astype(int)
    for col in fin_df.columns[1:]:
        fin_df[col] = pd.to_numeric(fin_df[col], errors='coerce')
    return fin_df

def attach_financial(df: pd.DataFrame, fin_df: pd.DataFrame) -> pd.DataFrame:
    return df.merge(fin_df, on='Round', how='left')

def kpi_options(df: pd.DataFrame, candidate_cols: list[str]) -> list[str]:
    """Return only the candidate columns that exist in df."""
    return [c for c in candidate_cols if c in df.columns]

# ------------------ Sidebar ------------------ #
st.sidebar.markdown("### Data source")
default_path = "TFC_0_6.xlsx"
data_source = st.sidebar.text_input(
    "Excel file path or *raw* GitHub URL",
    value=default_path,
    help="""Put your data file next to *streamlit_app.py* in the GitHub repo
    and leave this as `TFC_0_6.xlsx`, or paste a raw‑GitHub link."""
)

sheets = load_excel(data_source)

# Build financial DF
if 'finance report' not in sheets:
    st.error("❌ Sheet 'finance report' not found in workbook.")
    st.stop()
fin_df = _extract_financial(sheets['finance report'])

# Core functional sheets
component_df = sheets.get('Component', pd.DataFrame())
supplier_df  = sheets.get('Supplier', pd.DataFrame())
product_df   = sheets.get('Product', pd.DataFrame())
warehouse_df = sheets.get('Warehouse, Salesarea', pd.DataFrame())

# Derived columns
if not component_df.empty:
    component_df['Raw Material Cost %'] = (
        component_df['Purchase value previous round'] /
        component_df.merge(fin_df, on='Round', how='left')['Realized Revenues'] * 100
    )
if not product_df.empty and 'Economic inventory (weeks)' in product_df.columns:
    product_df['Attained Shelf Life (weeks)'] = product_df['Economic inventory (weeks)']

# ------------------ Tabs ------------------ #
tab_purchase, tab_sales, tab_sc, tab_ops = st.tabs(
    ["Purchase", "Sales", "Supply Chain", "Operations"])

# ---- Purchase Tab ---- #
with tab_purchase:
    if component_df.empty:
        st.warning("Sheet 'Component' not found.")
    else:
        st.header("Purchase KPIs vs Financial Impact")
        df = attach_financial(component_df, fin_df)
        kpis = kpi_options(df, [
            'Delivery reliability (%)',
            'Rejection (%)',
            'Obsoletes (%)',
            'Raw Material Cost %'
        ])
        fin_kpi = st.selectbox("Pick financial KPI", ['ROI','Realized Revenues','COGS','Indirect Cost'])
        metric = st.selectbox("Pick Purchase KPI", kpis)
        fig = px.scatter(
            df, x=metric, y=fin_kpi,
            color='Component', hover_data=['Round'],
            title=f"{metric} vs {fin_kpi}")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df[[ 'Component', 'Round', metric, fin_kpi ]])

# ---- Sales Tab ---- #
with tab_sales:
    if product_df.empty:
        st.warning("Sheet 'Product' not found.")
    else:
        st.header("Sales KPIs vs Financial Impact")
        df = attach_financial(product_df, fin_df)
        sales_metrics = kpi_options(df, [
            'Attained Shelf Life (weeks)',
            'Service level (pieces)',
            'Forecast error (MAPE)',
            'Obsoletes (%)'
        ])
        fin_kpi = st.selectbox("Financial KPI", ['ROI','Realized Revenues','COGS','Indirect Cost'], key='sales_fin')
        metric = st.selectbox("Sales KPI", sales_metrics, key='sales_fun')
        fig = px.scatter(
            df, x=metric, y=fin_kpi,
            color='Product', hover_data=['Round'],
            title=f"{metric} vs {fin_kpi}")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df[['Product','Round',metric,fin_kpi]])

# ---- Supply Chain Tab ---- #
with tab_sc:
    st.header("Supply Chain KPIs vs Financial Impact")
    if component_df.empty or product_df.empty:
        st.warning("Component/Product sheets missing.")
    else:
        # merge component availability & product availability proxies
        comp_kpi = attach_financial(component_df[['Component','Round','Component availability (%)']], fin_df)
        prod_kpi = attach_financial(product_df[['Product','Round','Service level (pieces)']].rename(columns={'Service level (pieces)': 'Product availability (%)'}), fin_df)
        st.subheader("Component availability")
        fin_kpi = st.selectbox("Financial KPI", ['ROI','Realized Revenues'], key='sc_fin1')
        fig1 = px.scatter(comp_kpi, x='Component availability (%)', y=fin_kpi,
                          color='Component', hover_data=['Round'],
                          title=f"Component availability vs {fin_kpi}")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Product availability (proxy: service level)")
        fin_kpi2 = st.selectbox("Financial KPI", ['ROI','Realized Revenues'], key='sc_fin2')
        fig2 = px.scatter(prod_kpi, x='Product availability (%)', y=fin_kpi2,
                          color='Product', hover_data=['Round'],
                          title=f"Product availability vs {fin_kpi2}")
        st.plotly_chart(fig2, use_container_width=True)

# ---- Operations Tab ---- #
with tab_ops:
    st.header("Operations KPIs vs Financial Impact")
    if warehouse_df.empty or product_df.empty:
        st.warning("Required sheets not found.")
    else:
        wh_df = attach_financial(warehouse_df, fin_df)
        prod_df = attach_financial(product_df, fin_df)
        ops_kpis = {
            'Inbound/Outbound Cube Utilization (%)': 'Cube utilization (%)',
            'Production Plan Adherence (%)': 'Production plan adherence (%)'
        }
        section = st.selectbox("Select KPI", list(ops_kpis.keys()))
        metric_col = ops_kpis[section]
        fin_kpi = st.selectbox("Financial KPI", ['ROI','COGS'], key='ops_fin')
        label_col = 'Warehouse' if metric_col == 'Cube utilization (%)' else 'Product'
        dff = wh_df if metric_col == 'Cube utilization (%)' else prod_df
        fig = px.scatter(
            dff, x=metric_col, y=fin_kpi,
            color=label_col, hover_data=['Round'],
            title=f"{metric_col} vs {fin_kpi}")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(dff[[label_col,'Round',metric_col,fin_kpi]])

st.sidebar.success("✔️ Dashboard ready – choose KPIs in each tab!")
