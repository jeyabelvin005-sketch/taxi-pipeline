# NYC Taxi Trips ELT Pipeline

End-to-end data pipeline that ingests NYC TLC taxi trip data + NYC weather, builds a tested star schema with dbt, and serves it for analytics.

## Architecture

```mermaid
flowchart LR
    A[TLC Parquet] -->|Python COPY| B[(raw.yellow_trips)]
    C[Open-Meteo API] -->|Python requests| D[(raw.weather)]
    E[Zone Lookup CSV] -->|dbt seed| F[(taxi_zone_lookup)]

    B --> G[stg_yellow_trips]
    D --> H[stg_weather]

    G --> I[fact_trips]
    G --> J[dim_date]
    H --> K[dim_weather]
    F --> L[dim_zones]

    I --> M[Metabase Dashboard]
    J --> M
    K --> M
    L --> M
```

## Star Schema

```mermaid
erDiagram
    fact_trips }o--|| dim_zones : "pickup_location_id"
    fact_trips }o--|| dim_zones : "dropoff_location_id"
    fact_trips }o--|| dim_weather : "pickup_date"
    fact_trips }o--|| dim_date : "pickup_date"

    fact_trips {
        timestamp pickup_at
        date pickup_date
        int pickup_location_id
        text pickup_borough
        numeric total_amount
        bool is_rainy
        bool is_snowy
    }
    dim_zones {
        int location_id PK
        text borough
        text zone
    }
    dim_weather {
        date weather_date PK
        numeric temp_max_c
        numeric precipitation_mm
    }
    dim_date {
        date date_day PK
        int year
        int month
        bool is_weekend
    }
```

## Tech Stack

- **Ingestion:** Python 3.11, pandas, pyarrow, requests, psycopg2
- **Storage:** PostgreSQL 16 (Docker)
- **Transform:** dbt-core 1.8.9 + dbt-postgres 1.8.2
- **BI:** Metabase (Docker)

## Data Layers

- **raw:** exact source shape, no transforms
- **staging:** renamed, cast, filtered to source month (`views`)
- **marts:** star schema — `fact_trips` + 3 dims (`tables`)

## Key Features

- **Idempotent ingestion** — re-running any month deletes and reloads
- **Fast bulk load** — PostgreSQL `COPY` for 3M rows (~80s vs 31min)
- **Data quality** — 11 dbt tests (`not_null`, `unique`, `accepted_values`)
- **Date hygiene** — filters bad dates (2002/2090 rows in TLC data)
- **Weather enrichment** — daily NYC weather joined to trips

## How to Run

```bash
docker compose up -d
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install dbt-core==1.8.9 dbt-postgres==1.8.2

python -m ingestion.load_trips --year 2024 --month 1
python -m ingestion.load_weather --year 2024 --month 1

dbt seed
dbt build --select +fact_trips
```

## Results (2024-01)

| Metric | Value |
|---|---|
| Trips | 2,964,606 |
| Weather days | 31 |
| Zones | 265 |
| dbt tests | 17 |
| Ingestion | ~80s (COPY) |
| Full build | ~34s |

## Roadmap

- [ ] Airflow DAG for scheduled runs
- [ ] Kafka streaming
- [ ] PySpark 12-month backfill
- [ ] GitHub Actions CI
- [ ] Cloud (S3 + BigQuery)
## Dashboard

![NYC Taxi Dashboard](docs/screenshots/dashboard.png)
