"""Export the dbt marts to CSV so the public dashboard can run without a
database connection.

Streamlit Community Cloud cannot reach a Postgres running in Docker on a
laptop. Rather than hosting the warehouse, the deployed dashboard reads a
snapshot committed to the repository, and says so on screen.

The warehouse remains the source of truth: this file is generated from it,
and CI rebuilds the whole pipeline against a real Postgres on every push.

    python scripts/export_snapshot.py
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
from sqlalchemy import create_engine, text

from config import database_url

OUT = ROOT / "data" / "snapshot"
OUT.mkdir(parents=True, exist_ok=True)

QUERIES = {
    "macro_annual": """
        select year, inflation_pct, inflation_3y_avg, gdp_growth_pct,
               gdp_per_capita_usd, unemployment_pct, mad_per_usd,
               mad_depreciation_pct, decade
        from analytics.mart_macro_annual
        where country_code = 'MAR'
        order by year
    """,
    "indicators": """
        select indicator_name, domain, unit_type, first_year, last_year,
               observation_count, observed_count, missing_count, coverage_pct
        from analytics.dim_indicator
        order by coverage_pct desc, indicator_name
    """,
    "missing_years": """
        select d.indicator_name, f.year
        from analytics.fct_indicator_observation f
        join analytics.dim_indicator d using (indicator_code)
        where f.is_missing
        order by d.indicator_name, f.year
    """,
}


def main() -> int:
    engine = create_engine(database_url(), future=True)

    with engine.connect() as conn:
        for name, sql in QUERIES.items():
            df = pd.read_sql(text(sql), conn)
            path = OUT / f"{name}.csv"
            df.to_csv(path, index=False)
            print(f"{name:16} {len(df):>4} rows  ->  {path.relative_to(ROOT)}")

    stamp = OUT / "generated_at.txt"
    stamp.write_text(datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC\n"),
                     encoding="utf-8")
    print(f"\nstamped {stamp.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
