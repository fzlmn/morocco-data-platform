"""Load flattened records into the raw schema in PostgreSQL.

The load is idempotent: the natural key (country_code, indicator_code, year)
carries a primary key, and inserts upsert on conflict. Running the pipeline
twice produces the same table as running it once.
"""

from __future__ import annotations

import logging

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config import database_url

log = logging.getLogger(__name__)

TABLE = "raw.worldbank_indicators"

# CREATE IF NOT EXISTS rather than relying on sql/init, because the init
# scripts only run when the Docker volume is created from empty.
DDL = """
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.worldbank_indicators (
    country_code         text        NOT NULL,
    country_name         text,
    indicator_code       text        NOT NULL,
    indicator_name       text,
    year                 integer     NOT NULL,
    value                numeric,
    unit                 text,
    obs_status           text,
    decimals             integer,
    source_last_updated  date,
    loaded_at            timestamptz NOT NULL,
    CONSTRAINT worldbank_indicators_pkey
        PRIMARY KEY (country_code, indicator_code, year)
);
"""

UPSERT = f"""
INSERT INTO {TABLE} (
    country_code, country_name, indicator_code, indicator_name,
    year, value, unit, obs_status, decimals,
    source_last_updated, loaded_at
) VALUES (
    :country_code, :country_name, :indicator_code, :indicator_name,
    :year, :value, :unit, :obs_status, :decimals,
    :source_last_updated, :loaded_at
)
ON CONFLICT (country_code, indicator_code, year) DO UPDATE SET
    country_name        = EXCLUDED.country_name,
    indicator_name      = EXCLUDED.indicator_name,
    value               = EXCLUDED.value,
    unit                = EXCLUDED.unit,
    obs_status          = EXCLUDED.obs_status,
    decimals            = EXCLUDED.decimals,
    source_last_updated = EXCLUDED.source_last_updated,
    loaded_at           = EXCLUDED.loaded_at;
"""


def get_engine() -> Engine:
    return create_engine(database_url(), future=True)


def ensure_table(engine: Engine) -> None:
    with engine.begin() as conn:
        for statement in filter(None, (s.strip() for s in DDL.split(";"))):
            conn.execute(text(statement))
    log.info("schema and table ready")


def load_records(engine: Engine, records: list[dict]) -> int:
    """Upsert records. Returns the row count in the table afterwards."""
    if not records:
        log.warning("nothing to load")
        return 0

    with engine.begin() as conn:
        conn.execute(text(UPSERT), records)
        total = conn.execute(text(f"SELECT count(*) FROM {TABLE}")).scalar_one()

    log.info("upserted %s records; table now holds %s rows", len(records), total)
    return total


def summarise(engine: Engine) -> None:
    """Print what is actually in the table - a cheap post-load sanity check."""
    query = text(f"""
        SELECT indicator_code,
               count(*)                          AS years,
               min(year)                         AS first_year,
               max(year)                         AS last_year,
               count(*) FILTER (WHERE value IS NULL) AS nulls
        FROM {TABLE}
        GROUP BY indicator_code
        ORDER BY indicator_code
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).all()

    print(f"\n{'indicator':22} {'years':>5} {'from':>6} {'to':>6} {'nulls':>6}")
    print("-" * 50)
    for r in rows:
        print(f"{r.indicator_code:22} {r.years:>5} {r.first_year:>6} "
              f"{r.last_year:>6} {r.nulls:>6}")
