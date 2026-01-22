# SG Job Profitability OS

Production-grade Streamlit app for SG job profitability, quoting discipline, delivery control, and capacity management.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Data placement

Place processed tables in `./data/processed/` (Parquet preferred; CSV supported):

- `fact_timesheet_day_enriched.parquet`
- `fact_job_task_month.parquet`
- `audit_revenue_reconciliation_job_month.parquet`
- `audit_unallocated_revenue.parquet`

## Build marts

```bash
python scripts/build_marts.py
```

Marts are materialised to `./data/marts/` and loaded by the app for speed.

## Run app

```bash
streamlit run app.py
```

## Deployment (Streamlit Cloud)

1. Push this repo to GitHub.
2. In Streamlit Cloud, set `DATA_DIR` to your mounted data path.
3. Ensure `requirements.txt` is installed.

## Guardrails

- Revenue rollups always use Σ `rev_alloc`.
- Quote rollups dedupe at `(job_no, task_name)` before summing.
- Rate rollups are computed as ratios of summed numerators/denominators.
- Utilisation and capacity default to excluding `task_name` containing "leave".

## Glossary

See `pages/8_Glossary_Method.py` for formulas and definitions.
