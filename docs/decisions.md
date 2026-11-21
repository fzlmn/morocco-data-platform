# Decision log

Why things are the way they are. One entry per real choice — what was picked,
what was rejected, and the reason. Three or four lines each.

This is the file to re-read before an interview.

**Format:**

```
## <date> — <the decision>
**Chose:** ...
**Rejected:** ...
**Why:** ...
```

---

## 2026-10-16 — PostgreSQL in Docker for local development
**Chose:** Postgres 16 in a container; Python, dbt and Streamlit run natively.
**Rejected:** Everything in containers; SQLite; DuckDB.
**Why:** Code that changes constantly needs a fast feedback loop, so it stays
native. The database barely changes once configured, and containerising it makes
`docker compose down -v` a ten-second reset — which matters when testing whether
the load is idempotent. Postgres over SQLite because dbt-postgres is the adapter
used in industry, and the project is meant to look like production.

---

## 2026-10-27 — Always pass an explicit `per_page` to the World Bank API
**Chose:** Request with `&per_page=500`, and assert that the number of records
received equals `meta["total"]` before anything is written.
**Rejected:** Looping over `meta["pages"]` one page at a time.
**Why:** The API defaults to 50 records per page. The Morocco CPI series has 66
records, so a default request returns 50 of them and drops 16 — with HTTP 200,
no error and no warning. The pipeline would have loaded an incomplete series
silently. A single large page is simpler than a paging loop at this volume, but
the assertion is what actually prevents the bug, so it matters more than which
of the two is used. If a series ever exceeds 500 records the assertion fails
loudly and the loop becomes necessary.

---

## 2026-10-27 — Source profile: World Bank FP.CPI.TOTL.ZG / MAR
**Observed:** 66 records covering 1960–2025 with no gaps, zero null values, and
no blank country codes. Source last updated 2026-10-08.
**Quality issues found:**
1. *Silent pagination* — see the entry above. This is the only real defect.
2. *Nested objects* — `indicator` and `country` arrive as dicts, not strings,
   so they must be unpacked before the row can go into a relational table.
3. *`date` is a string*, not a number or a date; cast to integer year.

**On nulls:** the inflation series is complete, which turned out to be the
exception. Across the five indicators now loaded: unemployment is missing 31 of
66 years and GDP growth 7, while inflation, GDP per capita and the exchange rate
have none. The schema therefore allows nulls in `value` and the dbt test on that
column is deliberately not `not_null` — a decision taken on principle before
there was any evidence for it, and since confirmed by the data. A missing year is a
real fact about the data, so nulls are kept rather than dropped or zero-filled —
zero would read as "no inflation that year", which is a false statement.

---

## 2026-10-27 — Plausibility check on the values
**Checked:** highest and lowest years against known history.
**Result:** the extremes look credible. The peak is 1974 at 17.6%, the year of
the first oil shock; 1977 (12.6%), 1981 (12.5%), 1982 (10.5%) and 1984 (12.5%)
fall in Morocco's pre- and early-structural-adjustment period. The lowest
readings are mild deflation in 1966 (-1.0%) and 1967 (-0.8%), with 2019 (0.3%)
and 2014 (0.4%) near zero in a low-inflation decade.
**Why it matters:** values in a plausible range mean the unit is being read
correctly — the indicator is an annual percentage, not an index level. An index
would have come through in the hundreds and been loaded without complaint.

---

## 2026-11-21 — Country code: use `countryiso3code`, not `country.id`
**Found by:** the `accepted_values` test on `stg_worldbank_indicators.country_code`,
which failed on the first `dbt test` run.
**The bug:** the extractor read `obs["country"]["id"]`, which is the **ISO-2**
code (`MA`). The adjacent `countryiso3code` field carries **ISO-3** (`MAR`).
Both are present in every observation and neither is labelled; nothing about the
response makes the difference obvious.
**Why it mattered:** the pipeline ran clean, the loader reported 330 rows, and
every number in the warehouse was correct. Only the country identifier was
wrong — which would have broken the moment a second country or any join on an
ISO-3 key was added, and would have been invisible until then.
**Fix:** read `countryiso3code`, falling back to `country.id` when it is empty
(aggregate regions such as "Arab World" leave it blank).
**The wider point:** this is the argument for schema tests. No exception was
raised, no count was off, and the exploration notebook had used the right field
back in October. A test that asserted a known truth about the data caught what
reading the code did not.

---

## 2026-10-27 — Natural key for World Bank observations
**Chose:** `(country_code, indicator_code, year)`.
**Rejected:** A surrogate auto-increment id as the only key; `year` alone.
**Why:** One observation is uniquely identified by those three columns, so they
are what makes a re-run idempotent — without them a second load duplicates
every row. `year` alone fails as soon as a second indicator or a second country
is added, which is planned.

---

<!--
Still to write:

## Why the loader is idempotent the way it is
   Truncate-and-load? Upsert on the natural key? What you rejected and why.

## The grain of the fact table
   What one row represents. What alternative you considered.
-->
