# The Fresh Connection KPI Dashboard

This Streamlit app visualises the link between **functional KPIs** (Purchase, Sales, Supply Chain, Operations) and **financial KPIs** across all six rounds of *The Fresh Connection* simulation.

## 🌟 Features

| Tab | What you can explore |
|-----|----------------------|
| **Purchase** | Supplier‑level delivery reliability, rejection %, obsolescence %, and raw‑material cost % vs ROI & Revenues |
| **Sales** | Product‑level shelf life, service level, forecasting error, obsolescence % vs financials |
| **Supply Chain** | Component & product availability vs ROI / Revenues |
| **Operations** | Inbound & outbound warehouse cube utilisation and production‑plan adherence vs COGS / ROI |

All charts are interactive (zoom, hover, select) thanks to Plotly.

## 🚀 1‑Click Deploy on Streamlit Cloud

1. **Fork** this repo (or create a new one) and upload your `TFC_0_6.xlsx` file.
2. In your repo, open **`streamlit_app.py`** and replace the placeholder in `DEFAULT_DATA_URL` with the raw GitHub link of the Excel file.
3. Click **“Deploy to Streamlit”**.  
   Streamlit Cloud will install the requirements and launch your dashboard automatically.

## 🛠️ Local Development

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 🗃️ Data Format

The app expects the exact sheet structure exported by *The Fresh Connection*:

- `finance report`
- `Supplier`
- `Component`
- `Product`
- `Customer`
- `Warehouse, Salesarea`

No manual cleaning is required – the parser handles everything automatically.

## 📄 License

MIT – free to use, modify, and share.
