import pandas as pd

from src.data.semantic import safe_quote_rollup


def test_quote_dedupe_rollup():
    df = pd.DataFrame({
        "job_no": ["J1", "J1", "J1"],
        "task_name": ["T1", "T1", "T2"],
        "quoted_time_total": [10, 10, 5],
        "quoted_amount_total": [100, 100, 50],
        "department_final": ["D1", "D1", "D1"],
    })
    rollup = safe_quote_rollup(df, ["department_final"])
    assert rollup.loc[0, "quoted_hours"] == 15
    assert rollup.loc[0, "quoted_amount"] == 150
