"""Run the whole pipeline: extract from source, land in PostgreSQL.

    python run_pipeline.py

Safe to run repeatedly - the load upserts on the natural key.
"""

from __future__ import annotations

import logging
import sys

from extract.worldbank import IncompleteSeriesError, extract_all
from load.postgres import ensure_table, get_engine, load_records, summarise


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")
    log = logging.getLogger("pipeline")

    log.info("extracting from the World Bank API")
    try:
        records = extract_all()
    except IncompleteSeriesError as exc:
        log.error("incomplete series, nothing loaded: %s", exc)
        return 1

    log.info("connecting to PostgreSQL")
    engine = get_engine()
    ensure_table(engine)
    load_records(engine, records)
    summarise(engine)

    log.info("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
