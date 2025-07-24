# TFC KPI Dashboard

Streamlit dashboard to explore how functional KPIs (Purchase, Sales, Supply Chain, Operations)
influence core financial outcomes (ROI, Revenues, COGS, Indirect Cost) in *The Fresh Connection*
business simulation.

## 📦 Quick start

```bash
# clone your repo
git clone https://github.com/<you>/tfc-dashboard.git
cd tfc-dashboard

# create & activate virtual env (optional)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# install requirements
pip install -r requirements.txt

# put the Excel file next to streamlit_app.py
cp ../TFC_0_6.xlsx .

# run!
streamlit run streamlit_app.py
```

## 🚀 Deploy to Streamlit Cloud

1. Push **all** files in this folder (including `TFC_0_6.xlsx`) to a public GitHub repo.
2. Go to <https://share.streamlit.io/> ➜ *New app* ➜ select your repo and branch ➜ hit **Deploy**.
3. The app launches automatically. If you store the Excel elsewhere, paste its *raw* GitHub
   URL into the sidebar.

## 📂 File overview
| File | Purpose |
|------|---------|
| `streamlit_app.py` | Main dashboard script |
| `requirements.txt` | Python dependencies |
| `README.md` | This guide |

Enjoy analysing your six‑round *Fresh Connection* journey!