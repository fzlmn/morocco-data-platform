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

<!--
Still to write — these three are the ones interviewers dig into:

## Data quality issues found during exploration
   What was wrong with the source data, and what you did about each one.

## Why the loader is idempotent the way it is
   Truncate-and-load? Upsert on a key? What you rejected and why.

## The grain of the fact table
   What one row represents. What the key is. What alternative you considered.
-->
