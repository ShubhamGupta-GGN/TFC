import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load from GitHub repo
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/shubhamgpta/TFC-Dashboard/main/TFC_0_6.xlsx"
    sheets = pd.read_excel(url, sheet_name=None)
    return sheets

sheets = load_data()
finance_df = sheets['finance report']

# Extract financial KPIs
rounds = list(range(1, 7))
roi = finance_df.iloc[1, 1:8].tolist()
revenue = finance_df.iloc[2, 1:8].tolist()
cogs = finance_df.iloc[3, 1:8].tolist()
indirect_costs = finance_df.iloc[4, 1:8].tolist()

# Create sidebar
st.sidebar.title("The Fresh Connection - Dashboard")
tab = st.sidebar.radio("Select Functional Area", ["Purchase", "Sales", "Supply Chain", "Operations"])

# Shared financial KPI chart
def financial_kpi_chart():
    st.subheader("Financial KPI Overview (Rounds 1-6)")
    fig, ax = plt.subplots()
    ax.plot(rounds, roi, marker='o', label="ROI")
    ax.plot(rounds, revenue, marker='s', label="Revenue")
    ax.plot(rounds, cogs, marker='^', label="COGS")
    ax.plot(rounds, indirect_costs, marker='x', label="Indirect Costs")
    ax.set_xlabel("Round")
    ax.set_ylabel("Value")
    ax.legend()
    st.pyplot(fig)

# Tab-specific content
if tab == "Purchase":
    st.title("Purchase KPIs")
    purchase_df = sheets["Supplier - Component"]
    st.line_chart(purchase_df.pivot(index="Round", columns="Supplier", values="Rejection (%)"))
    st.line_chart(purchase_df.pivot(index="Round", columns="Supplier", values="Order size"))
    financial_kpi_chart()

elif tab == "Sales":
    st.title("Sales KPIs")
    sales_df = sheets["Customer"]
    st.line_chart(sales_df.pivot(index="Round", columns="Customer", values="Service level (pieces)"))
    st.line_chart(sales_df.pivot(index="Round", columns="Customer", values="Attained shelf life (%)"))
    financial_kpi_chart()

elif tab == "Supply Chain":
    st.title("Supply Chain KPIs")
    product_df = sheets["Product"]
    st.line_chart(product_df.pivot(index="Round", columns="Product", values="Service level (pieces)"))
    st.line_chart(product_df.pivot(index="Round", columns="Product", values="Economic inventory (weeks)"))
    financial_kpi_chart()

elif tab == "Operations":
    st.title("Operations KPIs")
    bottling_df = sheets["Bottling line"]
    st.line_chart(bottling_df.pivot(index="Round", columns="Bottling line", values="Production plan adherence (%)"))
    wh_df = sheets["Warehouse, Salesarea"]
    st.line_chart(wh_df.pivot(index="Round", columns="Warehouse", values="Cube utilization (%)"))
    financial_kpi_chart()
