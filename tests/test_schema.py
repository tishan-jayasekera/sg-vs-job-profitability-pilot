import pandas as pd
import pytest

from src.data.schema import validate_fact_timesheet


def test_schema_missing_columns():
    df = pd.DataFrame({"department_final": ["A"]})
    with pytest.raises(ValueError):
        validate_fact_timesheet(df)
