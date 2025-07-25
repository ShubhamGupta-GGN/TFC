import streamlit as st
import pandas as pd
import plotly.express as px

# GitHub raw URL base - replace with your repo's raw path
base_url = "https://raw.githubusercontent.com/yourusername/your-repo/main/data/"

# Load all datasets
@st.cache_data
def load_data():
    return {
        "finance": pd.read_csv(base_url + "finance_report.csv"),
        "supplier": pd.read_csv(base_url + "supplier.csv"),
        "product": pd.read_csv(base_url + "product.csv"),
        "customer": pd.read_csv(base_url + "customer.csv"),
        "component": pd.read_csv(base_url + "component.csv"),
        "supplier_component": pd.read_csv(base_url + "supplier_component.csv"),
        "warehouse": pd.read_csv(base_url + "warehouse.csv"),
        "bottling": pd.read_csv(base_url + "bottling_line.csv"),
        "mixers": pd.read_csv(base_url + "mixers.csv")
    }

data = load_data()

st.set_page_config(page_title="The Fresh Connection Dashboard", layout="wide")
st.title("📊 The Fresh Connection KPI Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(["🛒 Purchase", "🧾 Sales", "📦 Supply Chain", "🏭 Operations"])

with tab1:
    st.header("Purchase KPIs and Financial Impact")
    supplier_df = data["supplier"]
    st.subheader("Component Delivery Reliability by Round")
    fig1 = px.line(supplier_df, x="Round", y="Delivery reliability (%)", color="Supplier", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Component Rejection % by Round")
    fig2 = px.line(supplier_df, x="Round", y="Rejection  (%)", color="Supplier", markers=True)
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.header("Sales KPIs and Financial Impact")
    product_df = data["product"]
    customer_df = data["customer"]

    st.subheader("Forecast Error (MAPE) by Product")
    fig3 = px.line(product_df, x="Round", y="Forecast error (MAPE)", color="Product", markers=True)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Service Level (pieces) by Customer")
    fig4 = px.line(customer_df, x="Round", y="Service level (pieces)", color="Customer", markers=True)
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.header("Supply Chain KPIs and Financial Impact")
    component_df = data["component"]
    product_df = data["product"]

    st.subheader("Component Availability by Round")
    fig5 = px.line(component_df, x="Round", y="Component availability (%)", color="Component", markers=True)
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Product Availability (OSA) by Round")
    fig6 = px.line(product_df, x="Round", y="OSA", color="Product", markers=True)
    st.plotly_chart(fig6, use_container_width=True)

with tab4:
    st.header("Operations KPIs and Financial Impact")
    warehouse_df = data["warehouse"]
    bottling_df = data["bottling"]

    st.subheader("Inbound Warehouse Cube Utilization")
    inbound_df = warehouse_df[warehouse_df["Warehouse"] == "Raw materials warehouse"]
    fig7 = px.line(inbound_df, x="Round", y="Cube utilization (%)", markers=True)
    st.plotly_chart(fig7, use_container_width=True)

    st.subheader("Production Plan Adherence (%)")
    fig8 = px.line(bottling_df, x="Round", y="Production plan adherence (%)", color="Bottling line", markers=True)
    st.plotly_chart(fig8, use_container_width=True)
