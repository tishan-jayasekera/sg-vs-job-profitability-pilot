from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

try:  # Streamlit optional for scripts/tests
    import streamlit as st

    def _cache_data(ttl: int):
        return st.cache_data(ttl=ttl)

except Exception:  # pragma: no cover - used outside Streamlit

    def _cache_data(ttl: int):
        def _decorator(fn):
            return fn

        return _decorator


SUPPORTED_EXTS = (".parquet", ".csv")


def _resolve_table_path(base_dir: Path, name: str) -> Path:
    for ext in SUPPORTED_EXTS:
        candidate = base_dir / f"{name}{ext}"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Missing {name} in {base_dir} (supported: {SUPPORTED_EXTS})")


@_cache_data(ttl=3600)
def load_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    if path.suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported file extension: {path.suffix}")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _find_anywhere(name: str) -> Path | None:
    root = _repo_root()
    for ext in SUPPORTED_EXTS:
        matches = list(root.rglob(f"{name}{ext}"))
        if matches:
            return matches[0]
    return None


def load_processed_table(data_dir: Path, name: str) -> pd.DataFrame:
    primary_dir = data_dir / "processed"
    try:
        path = _resolve_table_path(primary_dir, name)
        return load_table(path)
    except FileNotFoundError:
        fallback_dir = _repo_root() / "data" / "processed"
        if fallback_dir != primary_dir:
            path = _resolve_table_path(fallback_dir, name)
            return load_table(path)
        found = _find_anywhere(name)
        if found:
            return load_table(found)
        raise


def load_mart_table(data_dir: Path, name: str, fallback_processed: Optional[str] = None) -> pd.DataFrame:
    mart_dir = data_dir / "marts"
    try:
        path = _resolve_table_path(mart_dir, name)
        return load_table(path)
    except FileNotFoundError:
        fallback_dir = _repo_root() / "data" / "marts"
        if fallback_dir != mart_dir:
            try:
                path = _resolve_table_path(fallback_dir, name)
                return load_table(path)
            except FileNotFoundError:
                pass
        found = _find_anywhere(name)
        if found:
            return load_table(found)
        if fallback_processed:
            return load_processed_table(data_dir, fallback_processed)
        raise
