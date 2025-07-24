
# The Fresh Connection KPI Impact Dashboard

Streamlit dashboard that visualises how functional KPIs (Purchase, Sales, Supply‑Chain, Operations)
drive the four key financial KPIs (ROI, Realised Revenues, COGS, Indirect Cost) across all rounds
of **The Fresh Connection** simulation.

## How to deploy (Streamlit Cloud)

1. **Create a new public GitHub repo** and upload:
   * `streamlit_app.py`
   * `requirements.txt`
   * `README.md`
   * `TFC_0_6.xlsx`  ← export from the game and place in repo root
2. Log into [Streamlit Cloud](https://share.streamlit.io), click **New app**, and select your repo.
3. Hit **Deploy** – that's it! The app opens at `/streamlit_app.py`.

**Tip:** If you prefer to keep the workbook outside the repo, delete it and supply a
*raw‑GitHub URL* (or any public URL) in the sidebar field at runtime.

## Local development

```bash
python -m venv .venv && source .venv/bin/activate  # or your OS equivalent
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Troubleshooting

* **Could not load Excel file** – Check the path/URL and that the repo is public.
* **Columns not found in data** – The column names in your export may differ; edit
  `clean_labels()` or the `default_metrics` lists to match.
