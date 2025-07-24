
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO

st.set_page_config(page_title="The Fresh Connection Dashboard", layout="wide")

# ---------- Helper functions ----------
def load_excel(source: str) -> dict[str, pd.DataFrame]:
    """Load an Excel from local path or raw‑GitHub URL and return a dict of DataFrames."""
    try:
        if source.startswith(("http://", "https://")):
            r = requests.get(source, timeout=10)
            r.raise_for_status()
            return pd.read_excel(BytesIO(r.content), sheet_name=None, engine="openpyxl")
        else:
            return pd.read_excel(source, sheet_name=None, engine="openpyxl")
    except Exception as e:
        st.error(
            "❌ Could not load the Excel file. "
            "Check that the path or URL is correct and publicly accessible.\n\n"
            f"Details: {e}"
        )
        st.stop()

def clean_labels(col: str) -> str:
    """Strip whitespace, lower, and normalise finance labels."""
    mapping = {
        "realized revenue": "Realized Revenues",
        "realised revenues": "Realized Revenues",
        "roi": "ROI",
        "cost of goods sold": "COGS",
        "cogs": "COGS",
        "indirect cost": "Indirect Cost",
    }
    c = col.strip()
    key = c.lower()
    return mapping.get(key, c)

def to_numeric(series: pd.Series) -> pd.Series:
    """Convert strings like '45%' or '1,234' to float."""
    return (
        pd.to_numeric(
            series.astype(str)
            .str.replace('%', '', regex=False)
            .str.replace(',', '', regex=False)
            .str.strip(),
            errors='coerce'
        )
    )

def safe_scatter(df: pd.DataFrame, x_col: str, y_col: str, color: str|None, hover: list[str]|None, title: str):
    """Plot scatter only if both columns exist and have numeric data."""
    missing = [c for c in [x_col, y_col] if c not in df.columns]
    if missing:
        st.warning(f"Columns not found in data: {', '.join(missing)}")
        return
    plot_df = df.copy()
    plot_df[x_col] = to_numeric(plot_df[x_col])
    plot_df[y_col] = to_numeric(plot_df[y_col])
    plot_df = plot_df.dropna(subset=[x_col, y_col])
    if plot_df.empty:
        st.warning("No numeric data available for this selection.")
        return
    fig = px.scatter(
        plot_df, x=x_col, y=y_col, color=color, hover_data=hover,
        title=title, template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------- Sidebar ----------
st.sidebar.header("Data source")
default_path = "TFC_0_6.xlsx"
data_source = st.sidebar.text_input(
    "Local file name **or** raw‑GitHub URL of your Excel export:",
    value=default_path
)

sheets = load_excel(data_source)

# ---------- Finance metrics ----------
finance_sheet = None
for name in sheets:
    if "finance" in name.lower():
        finance_sheet = sheets[name]
        break
if finance_sheet is None:
    st.error("No sheet containing 'finance' found in the workbook.")
    st.stop()

fin_df = finance_sheet.copy()
fin_df.columns = [clean_labels(c) for c in fin_df.columns]
# Expecting a column 'Round' to join on. If not, reset index.
if 'Round' not in fin_df.columns:
    fin_df = fin_df.rename(columns={fin_df.columns[0]: 'Round'})
# Keep only the four KPI cols plus round
keep_cols = ['Round', 'ROI', 'Realized Revenues', 'COGS', 'Indirect Cost']
fin_df = fin_df[[c for c in keep_cols if c in fin_df.columns]].copy()
for col in keep_cols[1:]:
    if col in fin_df.columns:
        fin_df[col] = to_numeric(fin_df[col])

# ---------- Tab builder ----------
def build_tab(tab_name: str, sheet_keywords: list[str], id_col: str, default_metrics: list[str]):
    with st.expander(f"ℹ️ About this tab", expanded=False):
        st.markdown(f"This view links **{tab_name} functional KPIs** with **financial results**.")
    # Find matching sheet
    target_sheet = None
    for name in sheets:
        if any(k in name.lower() for k in sheet_keywords):
            target_sheet = sheets[name]
            break
    if target_sheet is None:
        st.warning(f"No worksheet matched keywords {sheet_keywords}.")
        return
    df = target_sheet.copy()
    if 'Round' not in df.columns:
        df = df.rename(columns={df.columns[0]: 'Round'})
    # Merge finance
    merged = pd.merge(df, fin_df, on='Round', how='left')
    numeric_cols = [c for c in merged.columns if merged[c].dtype != 'object' and c not in ['Round']]
    # Interface
    metric = st.selectbox("Functional KPI (x‑axis)", options=[c for c in numeric_cols if c not in keep_cols], index=0)
    fin_kpi = st.selectbox("Financial KPI (y‑axis)", options=[c for c in keep_cols if c != 'Round' and c in merged.columns], index=0)
    safe_scatter(merged, metric, fin_kpi, color=id_col if id_col in merged.columns else None, hover=['Round'], title=f"{metric} vs {fin_kpi}")
    st.dataframe(merged.head(30))

# ---------- Dashboard ----------
st.title("📊 The Fresh Connection – KPI Impact Dashboard")
tab_purchase, tab_sales, tab_supply, tab_ops = st.tabs(["Purchase", "Sales", "Supply Chain", "Operations"])

with tab_purchase:
    build_tab(
        tab_name="Purchase",
        sheet_keywords=["component", "purchase"],
        id_col="Component",
        default_metrics=["Component Delivery Reliability", "Component Rejection percentage", "Component Obsolete percentage", "Raw Material Cost %"]
    )

with tab_sales:
    build_tab(
        tab_name="Sales",
        sheet_keywords=["product", "sales"],
        id_col="Customer" if any("customer" in s.lower() for s in sheets) else "Product",
        default_metrics=["Product Average Attained Shelf Life", "Product Average Achieved Service Level", "Product Average Forecasting Error", "Product Obsolescence percent"]
    )

with tab_supply:
    build_tab(
        tab_name="Supply Chain",
        sheet_keywords=["supply", "availability"],
        id_col="Component" if "Component" in sheets else "Product",
        default_metrics=["Component availability", "product availability"]
    )

with tab_ops:
    build_tab(
        tab_name="Operations",
        sheet_keywords=["warehouse", "production", "operations"],
        id_col="Area" if "Area" in sheets else "Product",
        default_metrics=["Inbound Warehouse Cube Utilization", "Outbound Warehouse Cube Utilization", "Production Plan Adherence Percentage"]
    )

st.caption("© Streamlit dashboard template by ChatGPT – Revised " + pd.Timestamp.utcnow().strftime('%Y-%m-%d'))
