# The Fresh Connection KPI Dashboard

This Streamlit dashboard visualizes key Functional and Financial KPIs across 6 rounds of "The Fresh Connection" simulation game.

## 🔧 Setup Instructions

### 1. Upload files to GitHub
Create a repository with the following structure:

```
/your-repo
│
├── app.py
├── requirements.txt
├── README.md
└── /data
    ├── finance_report.csv
    ├── supplier.csv
    ├── product.csv
    ├── customer.csv
    ├── component.csv
    ├── supplier_component.csv
    ├── warehouse.csv
    ├── bottling_line.csv
    └── mixers.csv
```

### 2. Deploy on Streamlit Cloud

1. Sign in at [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Click **New App** ➝ Connect your GitHub repo
3. Set **Main file path** to `app.py`
4. Click **Deploy**

## 📊 Tabs Overview

### Purchase
- Component Delivery Reliability
- Rejection % / Obsolete %
- Raw Material Cost %
- Impact on ROI and COGS

### Sales
- Shelf Life, Service Levels
- Forecasting Error
- Product Obsolescence
- Revenue and ROI contribution

### Supply Chain
- Component & Product Availability
- Revenue and ROI by product/component

### Operations
- Inbound & Outbound Warehouse Utilization
- Production Plan Adherence
- Impact on ROI and COGS
