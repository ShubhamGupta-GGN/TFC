import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO

st.set_page_config(page_title="The Fresh Connection KPI Dashboard", layout="wide")

# ---------------------------------------------------------------------------
# 🗂️ Configuration
# ---------------------------------------------------------------------------
# Update this with the raw GitHub URL of your simulation data file (TFC_0_6.xlsx)
DEFAULT_DATA_URL = "https://raw.githubusercontent.com/<your‑username>/<your‑repo>/main/TFC_0_6.xlsx"

data_url = st.sidebar.text_input(
    "📂 Paste raw GitHub URL of `TFC_0_6.xlsx`",
    value=DEFAULT_DATA_URL,
    help="The dashboard pulls fresh data from this link every time it reloads.",
)

@st.cache_data(show_spinner=False)
def load_excel(url: str):
    """Download the Excel file from GitHub and return a dict of DataFrames."""
    bytes_data = requests.get(url).content
    xls = pd.ExcelFile(BytesIO(bytes_data))
    sheets = {
        name: pd.read_excel(xls, sheet_name=name)
        for name in [
            "finance report",
            "Supplier",
            "Component",
            "Product",
            "Customer",
            "Warehouse, Salesarea",
        ]
    }
    return sheets

def parse_financial(fin_mat: pd.DataFrame) -> pd.DataFrame:
    """Extract ROI, Realized Revenues, COGS, and Indirect Cost for each round."""
    cols = list(range(1, 8))  # columns 1‑7 are the values for rounds 0‑6
    rounds = list(range(0, 7))
    out = pd.DataFrame({ "Round": rounds })

    # Helper function
    def first_match(pattern:str):
        return fin_mat[ fin_mat[0].astype(str).str.match(pattern) ]

    # ROI
    roi_row = first_match(r"^ROI$")
    if not roi_row.empty:
        out["ROI"] = roi_row.iloc[0, cols].astype(float).values

    # Realized revenue
    rr_row = first_match(r"^Realized revenue$")
    if rr_row.empty:
        rr_row = first_match(r"^Realized revenue$")  # fallback
    if not rr_row.empty:
        out["Realized Revenues"] = rr_row.iloc[0, cols].astype(float).values

    # Aggregate COGS & Indirect Cost
    cogs_rows = fin_mat[0].astype(str).str.contains("Cost of goods sold", na=False)
    out["COGS"] = (
        fin_mat.loc[cogs_rows, cols]
        .apply(pd.to_numeric, errors="coerce")
        .sum()
        .values
    )

    ind_rows = fin_mat[0].astype(str).str.contains("Indirect cost", na=False)
    out["Indirect Cost"] = (
        fin_mat.loc[ind_rows, cols]
        .apply(pd.to_numeric, errors="coerce")
        .sum()
        .values
    )

    return out

def compute_purchase_metrics(df: pd.DataFrame) -> pd.DataFrame:
    total_purchase = df.groupby("Round")["Purchase  value previous round"].transform("sum")
    df = df.copy()
    df["Raw Material Cost %"] = df["Purchase  value previous round"] / total_purchase
    return df

# ---------------------------------------------------------------------------
# ⏬ Data Load
# ---------------------------------------------------------------------------
with st.spinner("Downloading & parsing data..."):
    sheets = load_excel(data_url)

supplier_df   = compute_purchase_metrics(sheets["Supplier"])
component_df  = sheets["Component"]
product_df    = sheets["Product"]
customer_df   = sheets["Customer"]
warehouse_df  = sheets["Warehouse, Salesarea"]
finance_df    = parse_financial(pd.read_excel(BytesIO(requests.get(data_url).content), sheet_name="finance report", header=None))

# Merge finance metrics into other dfs for scatter analysis
def attach_financial(df, on="Round"):
    return df.merge(finance_df, on=on, how="left")

# ---------------------------------------------------------------------------
# 📊 Dashboard Tabs
# ---------------------------------------------------------------------------
tabs = st.tabs(["🛒 Purchase", "🛍️ Sales", "🚚 Supply Chain", "🏭 Operations"])

# ---------------------------------------------------------------------------
# 1️⃣ Purchase Tab
# ---------------------------------------------------------------------------
with tabs[0]:
    st.header("Purchase KPIs vs Financial Impact")

    metric = st.selectbox(
        "Choose functional KPI",
        [
            "Delivery reliability (%)",
            "Rejection  (%)",
            "Obsoletes (%)",
            "Raw Material Cost %",
        ],
    )
    round_sel = st.slider("Round", min_value=0, max_value=6, value=0, step=1)
    data = attach_financial(supplier_df)
    sub = data[data["Round"] == round_sel]

    col1, col2 = st.columns([2, 2])
    with col1:
        fig = px.scatter(
            sub,
            x=metric,
            y="ROI",
            color="Supplier",
            size="Purchase  value previous round",
            hover_name="Supplier",
            title=f"{metric} vs ROI (Round {round_sel})",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        kpi_trend = (
            supplier_df.groupby("Round")[metric]
            .mean()
            .reset_index()
            .rename(columns={metric: "Average"})
        )
        fig2 = px.line(
            kpi_trend,
            x="Round",
            y="Average",
            markers=True,
            title=f"Average {metric} Across Rounds",
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(sub[["Supplier", metric, "Raw Material Cost %", "ROI", "Realized Revenues", "COGS", "Indirect Cost"]])

# ---------------------------------------------------------------------------
# 2️⃣ Sales Tab
# ---------------------------------------------------------------------------
with tabs[1]:
    st.header("Sales KPIs vs Financial Impact")

    metric = st.selectbox(
        "Choose functional KPI",
        [
            "Attained shelf life (%)",
            "Service level (pieces)",
            "Forecast error (MAPE)",
            "Obsoletes (%)",
        ],
        key="sales_metric",
    )
    round_sel = st.slider("Round ", 0, 6, 0, key="sales_round")

    # Aggregate to product level
    data = attach_financial(product_df)[["Product", "Round", metric, "ROI", "Realized Revenues"]]
    sub = data[data["Round"] == round_sel]

    fig = px.scatter(
        sub,
        x=metric,
        y="Realized Revenues",
        color="Product",
        hover_name="Product",
        title=f"{metric} vs Realized Revenues (Round {round_sel})",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(sub)

# ---------------------------------------------------------------------------
# 3️⃣ Supply Chain Tab
# ---------------------------------------------------------------------------
with tabs[2]:
    st.header("Supply Chain KPIs vs Financial Impact")

    metric = st.selectbox(
        "Choose functional KPI",
        [
            "Component availability (%)",
            "Service level (pieces)",
        ],
        key="sc_metric",
    )
    round_sel = st.slider("Round  ", 0, 6, 0, key="sc_round")

    if metric == "Component availability (%)":
        df = attach_financial(component_df)[["Component", "Round", metric, "ROI", "Realized Revenues"]]
        id_field = "Component"
    else:
        df = attach_financial(product_df)[["Product", "Round", "Service level (pieces)", "ROI", "Realized Revenues"]]
        id_field = "Product"

    sub = df[df["Round"] == round_sel]
    fig = px.scatter(
        sub,
        x=metric,
        y="Realized Revenues",
        color=id_field,
        title=f"{metric} vs Realized Revenues (Round {round_sel})",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(sub)

# ---------------------------------------------------------------------------
# 4️⃣ Operations Tab
# ---------------------------------------------------------------------------
with tabs[3]:
    st.header("Operations KPIs vs Financial Impact")

    # Identify inbound & outbound warehouses
    inbound = warehouse_df[warehouse_df["Warehouse"] == "Raw materials warehouse"]
    outbound = warehouse_df[warehouse_df["Warehouse"] == "Finished goods warehouse"]

    # Cube util
    inbound_util = attach_financial(inbound)[["Round", "Cube utilization (%)", "ROI", "COGS"]]
    outbound_util = attach_financial(outbound)[["Round", "Cube utilization (%)", "ROI", "COGS"]]

    prod_plan = attach_financial(product_df)[["Round", "Production plan adherence (%)", "ROI", "COGS"]]

    st.subheader("Inbound vs Outbound Cube Utilization vs COGS")

    fig = px.line(
        inbound_util,
        x="Round",
        y="Cube utilization (%)",
        markers=True,
        label="Inbound",
        title="Inbound & Outbound Warehouse Cube Utilization Over Rounds",
    )
    fig.add_scatter(
        x=outbound_util["Round"],
        y=outbound_util["Cube utilization (%)"],
        mode="lines+markers",
        name="Outbound",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Production Plan Adherence Trend")
    fig2 = px.line(
        prod_plan,
        x="Round",
        y="Production plan adherence (%)",
        markers=True,
        title="Production Plan Adherence (%) Across Rounds",
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(prod_plan)

st.caption("© Powered by Streamlit • The Fresh Connection KPI Dashboard")
