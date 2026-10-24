import argparse
import io
import logging
import time
from pathlib import Path

import pandas as pd
import requests
from sqlalchemy import create_engine, text

from ingestion.config import DB_URL, DATA_DIR, TLC_BASE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("ingest.trips")


def download(year: int, month: int, retries: int = 3) -> Path:
    fname = f"yellow_tripdata_{year}-{month:02d}.parquet"
    dest = Path(DATA_DIR) / fname
    if dest.exists():
        log.info("already present, skip download: %s", dest)
        return dest

    url = f"{TLC_BASE}/{fname}"
    dest.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, retries + 1):
        try:
            with requests.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                tmp = dest.with_suffix(".part")
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        f.write(chunk)
                tmp.rename(dest)
            log.info("downloaded %s (%.1f MB)", dest, dest.stat().st_size / 1e6)
            return dest
        except Exception as e:
            log.warning("attempt %d/%d failed: %s", attempt, retries, e)
            if attempt == retries:
                raise
            time.sleep(5 * attempt)


def load(path: Path, year: int, month: int) -> int:
    source_month = f"{year}-{month:02d}"
    df = pd.read_parquet(path)
    df.columns = [c.strip().lower() for c in df.columns]
    df["source_month"] = source_month

    engine = create_engine(DB_URL)

    # ensure table + idempotent delete
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
        exists = conn.execute(
            text("SELECT to_regclass('raw.yellow_trips')")
        ).scalar()
        if not exists:
            df.head(0).to_sql(
                "yellow_trips", engine, schema="raw",
                if_exists="fail", index=False,
            )
        conn.execute(
            text("DELETE FROM raw.yellow_trips WHERE source_month = :m"),
            {"m": source_month},
        )

    # fast bulk load via COPY
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False, na_rep="\\N")
    buf.seek(0)

    raw = engine.raw_connection()
    try:
        with raw.cursor() as cur:
            cur.copy_expert(
                "COPY raw.yellow_trips FROM STDIN WITH (FORMAT csv, NULL '\\N')",
                buf,
            )
        raw.commit()
    finally:
        raw.close()

    log.info("loaded %d rows for %s", len(df), source_month)
    return len(df)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--month", type=int, required=True)
    a = p.parse_args()
    path = download(a.year, a.month)
    load(path, a.year, a.month)


if __name__ == "__main__":
    main()