import pandas as pd


def test_reconciliation_within_tolerance():
    fact = pd.DataFrame({
        "job_no": ["J1", "J1"],
        "month_key": ["2024-01", "2024-01"],
        "rev_alloc": [100, 200],
    })
    audit = pd.DataFrame({
        "job_no": ["J1"],
        "month_key": ["2024-01"],
        "rev_alloc_total": [300],
        "revenue_pool_total": [300],
        "diff": [0],
    })
    alloc = fact.groupby(["job_no", "month_key"], dropna=False)["rev_alloc"].sum().reset_index()
    merged = alloc.merge(audit, on=["job_no", "month_key"], how="left")
    tolerance = 1e-6
    assert (merged["rev_alloc_total"] - merged["rev_alloc"]).abs().max() <= tolerance
