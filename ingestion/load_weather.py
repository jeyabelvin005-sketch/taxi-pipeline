import argparse
import logging
from datetime import date

import pandas as pd
import requests
from sqlalchemy import create_engine, text

from ingestion.config import DB_URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("ingest.weather")

# NYC coordinates
LAT = 40.7128
LON = -74.0060
API = "https://archive-api.open-meteo.com/v1/archive"
DAILY_VARS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "snowfall_sum",
    "wind_speed_10m_max",
]


def fetch(start: date, end: date, retries: int = 3) -> pd.DataFrame:
    params = {
        "latitude": LAT,
        "longitude": LON,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": ",".join(DAILY_VARS),
        "timezone": "America/New_York",
    }

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(API, params=params, timeout=60)
            r.raise_for_status()
            payload = r.json()
            daily = payload["daily"]
            df = pd.DataFrame(daily)
            df = df.rename(columns={"time": "weather_date"})
            log.info("fetched %d days (%s to %s)", len(df), start, end)
            return df
        except Exception as e:
            log.warning("attempt %d/%d failed: %s", attempt, retries, e)
            if attempt == retries:
                raise
            import time
            time.sleep(5 * attempt)


def load(df: pd.DataFrame, start: date, end: date) -> int:
    engine = create_engine(DB_URL)

    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
        exists = conn.execute(
            text("SELECT to_regclass('raw.weather')")
        ).scalar()
        if not exists:
            df.head(0).to_sql(
                "weather", engine, schema="raw",
                if_exists="fail", index=False,
            )
        conn.execute(
            text(
                "DELETE FROM raw.weather "
                "WHERE weather_date BETWEEN :s AND :e"
            ),
            {"s": start.isoformat(), "e": end.isoformat()},
        )

    df.to_sql(
        "weather", engine, schema="raw",
        if_exists="append", index=False, chunksize=500,
    )
    log.info("loaded %d rows into raw.weather", len(df))
    return len(df)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--month", type=int, required=True)
    a = p.parse_args()

    import calendar
    start = date(a.year, a.month, 1)
    end = date(a.year, a.month, calendar.monthrange(a.year, a.month)[1])

    df = fetch(start, end)
    load(df, start, end)


if __name__ == "__main__":
    main()