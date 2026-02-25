from __future__ import annotations

from datetime import datetime
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

DATA_DIR = Path("data/parquet")


def _generate_ohlcv(pair: str, start: datetime, end: datetime) -> pd.DataFrame:
    index = pd.date_range(start=start, end=end, freq="1h", inclusive="left")
    seed = abs(hash(pair)) % (2**32)
    rng = np.random.default_rng(seed)
    returns = rng.normal(loc=0.0001, scale=0.01, size=len(index))
    close = 100 * np.exp(np.cumsum(returns))
    open_ = np.roll(close, 1)
    open_[0] = close[0]
    high = np.maximum(open_, close) * (1 + rng.uniform(0, 0.005, len(index)))
    low = np.minimum(open_, close) * (1 - rng.uniform(0, 0.005, len(index)))
    volume = rng.uniform(1000, 5000, len(index))
    return pd.DataFrame(
        {
            "timestamp": index,
            "pair": pair,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def ensure_parquet_dataset(pairs: list[str], start: datetime, end: datetime) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for pair in pairs:
        file_path = DATA_DIR / f"{pair}.parquet"
        if file_path.exists():
            continue
        df = _generate_ohlcv(pair, start, end)
        df.to_parquet(file_path, index=False)


def load_pair_data(pairs: list[str], start: datetime, end: datetime) -> pd.DataFrame:
    ensure_parquet_dataset(pairs, start, end)
    con = duckdb.connect()
    files = [str(DATA_DIR / f"{pair}.parquet") for pair in pairs]
    query = """
    SELECT *
    FROM read_parquet($files)
    WHERE timestamp >= $start AND timestamp <= $end
    ORDER BY timestamp
    """
    df = con.execute(query, {"files": files, "start": start, "end": end}).df()
    con.close()
    return df
