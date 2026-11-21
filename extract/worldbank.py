"""Extract indicator series for one country from the World Bank API.

The API paginates at 50 records by default and truncates silently: a short
response still returns HTTP 200 with no warning. Every fetch here therefore
asserts that the number of records received matches the total the API reports,
and raises rather than returning a partial series.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import COUNTRY, INDICATORS, PER_PAGE, RAW_DIR, WORLDBANK_BASE

log = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30


class IncompleteSeriesError(RuntimeError):
    """Raised when the API returns fewer records than it says exist."""


def _session() -> requests.Session:
    """A session that retries transient failures instead of giving up."""
    retry = Retry(
        total=4,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def fetch_indicator(
    indicator: str,
    country: str = COUNTRY,
    per_page: int = PER_PAGE,
    session: requests.Session | None = None,
) -> tuple[dict, list[dict]]:
    """Fetch one complete indicator series.

    Returns the metadata object and the list of observations. Raises
    IncompleteSeriesError if the response is short.
    """
    session = session or _session()
    url = f"{WORLDBANK_BASE}/country/{country}/indicator/{indicator}"
    params = {"format": "json", "per_page": per_page}

    response = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()

    # The response is a two-element list: [metadata, observations].
    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError(f"{indicator}: unexpected response shape: {payload!r:.200}")

    meta, observations = payload[0], payload[1] or []

    expected = meta.get("total", 0)
    if len(observations) != expected:
        raise IncompleteSeriesError(
            f"{indicator}: API reports {expected} records but returned "
            f"{len(observations)}. Raise per_page (currently {per_page}) or "
            f"page through meta['pages'] ({meta.get('pages')})."
        )

    log.info("%s: %s records (%s-%s)", indicator, len(observations),
             observations[-1]["date"] if observations else "-",
             observations[0]["date"] if observations else "-")
    return meta, observations


def save_raw(indicator: str, payload: list, country: str = COUNTRY) -> Path:
    """Persist the untouched response so a reload never needs the network."""
    path = RAW_DIR / f"worldbank_{country}_{indicator}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def to_records(meta: dict, observations: list[dict]) -> list[dict]:
    """Flatten observations into flat rows ready for the raw table."""
    loaded_at = datetime.now(timezone.utc)
    source_updated = meta.get("lastupdated")

    rows = []
    for obs in observations:
        # `countryiso3code` is the ISO-3 code ("MAR"); obs["country"]["id"] is
        # ISO-2 ("MA"). They are both present and they are not the same field.
        # Aggregate regions leave countryiso3code empty, hence the fallback.
        country_code = (obs.get("countryiso3code") or "").strip() \
            or obs["country"]["id"]

        rows.append({
            "country_code": country_code,
            "country_name": obs["country"]["value"],
            "indicator_code": obs["indicator"]["id"],
            "indicator_name": obs["indicator"]["value"],
            "year": int(obs["date"]),
            "value": obs["value"],
            "unit": obs.get("unit") or None,
            "obs_status": obs.get("obs_status") or None,
            "decimals": obs.get("decimal"),
            "source_last_updated": source_updated,
            "loaded_at": loaded_at,
        })
    return rows


def extract_all(indicators: dict[str, str] | None = None) -> list[dict]:
    """Fetch every configured indicator, save raw, return flattened rows."""
    indicators = indicators or INDICATORS
    session = _session()
    all_rows: list[dict] = []

    for indicator in indicators:
        meta, observations = fetch_indicator(indicator, session=session)
        save_raw(indicator, [meta, observations])
        all_rows.extend(to_records(meta, observations))

    return all_rows


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    rows = extract_all()
    print(f"\nextracted {len(rows)} rows across {len(INDICATORS)} indicators")
