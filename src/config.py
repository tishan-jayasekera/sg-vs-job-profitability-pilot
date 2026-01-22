from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _get_env(name: str, default: str) -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class AppConfig:
    data_dir: Path
    app_env: str
    cache_ttl_seconds: int
    active_job_recency_days: int
    active_staff_recency_months: int
    recency_half_life_months: int


def load_config() -> AppConfig:
    data_dir = Path(_get_env("DATA_DIR", "./data"))
    return AppConfig(
        data_dir=data_dir,
        app_env=_get_env("APP_ENV", "dev"),
        cache_ttl_seconds=int(_get_env("CACHE_TTL_SECONDS", "3600")),
        active_job_recency_days=int(_get_env("ACTIVE_JOB_RECENCY_DAYS", "21")),
        active_staff_recency_months=int(_get_env("ACTIVE_STAFF_RECENCY_MONTHS", "6")),
        recency_half_life_months=int(_get_env("RECENCY_HALF_LIFE_MONTHS", "6")),
    )
