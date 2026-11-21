# How the pipeline works

Line-by-line notes on `extract/worldbank.py` and `load/postgres.py`.
Read this before changing either file.

---

## 1. The retry session

```python
retry = Retry(
    total=4,                      # → give up after 4 attempts, not forever
    backoff_factor=1.5,           # → wait 1.5s, 3s, 6s, 12s between tries
    status_forcelist=(429, 500, 502, 503, 504),
                                  # → only retry these: rate-limit + server errors
    allowed_methods=frozenset(["GET"]),
                                  # → never auto-retry POST/PUT (not idempotent)
)
session = requests.Session()      # → reuse one TCP connection for all 5 indicators
session.mount("https://", HTTPAdapter(max_retries=retry))
                                  # → attach the retry policy to every https call
```

**Why:** a 500 from the API is usually transient. Without retries one blip kills
the whole run. 404 and 400 are *not* in the list — those mean the request itself
is wrong, and retrying a wrong request just wastes time.

---

## 2. Fetching, and the check that matters

```python
response = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
                                  # → params= lets requests build the query string
                                  #   and URL-encode it; safer than f-strings
response.raise_for_status()       # → turn a 4xx/5xx into an exception
payload = response.json()         # → parse JSON into Python objects
```

```python
if not isinstance(payload, list) or len(payload) < 2:
    raise ValueError(...)         # → fail loudly if the shape ever changes
meta, observations = payload[0], payload[1] or []
                                  # → [metadata, observations]; `or []` guards
                                  #   against null when a series is empty
```

```python
expected = meta.get("total", 0)   # → how many records the API says exist
if len(observations) != expected: # → how many actually arrived
    raise IncompleteSeriesError(...)
```

**This is the whole point of the file.** The API defaults to 50 records per
page and returns HTTP 200 for a truncated response — no error, no warning. The
exploration notebook found that a default request dropped 16 of 66 records.
`per_page=1000` fixes it today; the assertion is what stops it coming back
silently if a series ever grows past 1000.

---

## 3. Flattening

```python
loaded_at = datetime.now(timezone.utc)
                                  # → one timestamp for the whole batch, so every
                                  #   row in a run shares it; timezone-aware, never naive
```

```python
"country_code": (obs.get("countryiso3code") or "").strip()
                 or obs["country"]["id"],
                                  # → countryiso3code is ISO-3 ("MAR");
                                  #   country["id"] is ISO-2 ("MA"). Not the same
                                  #   field. The fallback covers aggregate regions,
                                  #   which leave countryiso3code empty.
"year": int(obs["date"]),         # → `date` arrives as a string: "2024" → 2024
"value": obs["value"],            # → left as-is; None stays None (a real gap)
"unit": obs.get("unit") or None,  # → the API sends "" not null; normalise to None
```

**Why `or None`:** an empty string and a null mean different things in SQL.
`"" IS NOT NULL` is true, so empty strings slip past null checks and show up as
blanks in the dashboard.

---

## 4. The upsert

```sql
CONSTRAINT worldbank_indicators_pkey
    PRIMARY KEY (country_code, indicator_code, year)
                                  -- → the natural key: one row per country,
                                  --    indicator and year. This is what makes
                                  --    the load idempotent.
```

```sql
INSERT INTO raw.worldbank_indicators (...) VALUES (:country_code, ...)
                                  -- → :name are bound parameters, filled by
                                  --    SQLAlchemy. Never string-format SQL.
ON CONFLICT (country_code, indicator_code, year) DO UPDATE SET
    value     = EXCLUDED.value,   -- → EXCLUDED is the row that was *going* to be
    loaded_at = EXCLUDED.loaded_at--    inserted; take the new value over the old
```

**Why upsert and not truncate-and-load:** truncating means the table is empty
for the duration of the load. If the run fails halfway, the table is left
wrong. The upsert never has an empty state, and a re-run after a revision
updates the changed values in place.

**Why not `INSERT ... ON CONFLICT DO NOTHING`:** the World Bank revises figures.
A year already in the table can legitimately get a new value, and `DO NOTHING`
would keep the stale one forever.

---

## 5. Executing

```python
with engine.begin() as conn:      # → opens a transaction; commits on clean exit,
                                  #   rolls back on any exception
    conn.execute(text(UPSERT), records)
                                  # → passing a LIST of dicts runs executemany:
                                  #   one round trip for all ~330 rows
```

Compare with `engine.connect()`, which does **not** commit — a frequent cause of
"the script ran fine but the table is empty".

---

## 6. Running it

```bash
docker compose up -d              # → start Postgres
python run_pipeline.py            # → extract, then load
python run_pipeline.py            # → run again: row count must not change
```

That second run is the idempotency test. If the count grows, the natural key
is wrong.
