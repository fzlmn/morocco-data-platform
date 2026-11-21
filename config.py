"""Shared configuration: paths, database URL, and which series to extract."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

RAW_DIR = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# --- World Bank -----------------------------------------------------------

WORLDBANK_BASE = "https://api.worldbank.org/v2"
COUNTRY = "MAR"

# A deliberately large page size. The API defaults to 50 and truncates without
# error; see docs/decisions.md, 2026-10-27.
PER_PAGE = 1000

INDICATORS: dict[str, str] = {
    "FP.CPI.TOTL.ZG": "Inflation, consumer prices (annual %)",
    "NY.GDP.MKTP.KD.ZG": "GDP growth (annual %)",
    "NY.GDP.PCAP.CD": "GDP per capita (current US$)",
    "SL.UEM.TOTL.ZS": "Unemployment, total (% of total labor force)",
    "PA.NUS.FCRF": "Official exchange rate (MAD per US$, period average)",
}

# --- Database -------------------------------------------------------------

def database_url() -> str:
    """Build the SQLAlchemy URL from environment variables."""
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.environ["POSTGRES_DB"]
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
