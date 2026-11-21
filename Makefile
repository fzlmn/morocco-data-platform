.PHONY: up down reset install pipeline build test dbt-docs dashboard all

# --- infrastructure ---
up:
	docker compose up -d

down:
	docker compose down

reset:
	docker compose down -v && docker compose up -d

install:
	pip install -r requirements.txt

# --- pipeline ---
pipeline:
	python run_pipeline.py

build:
	dbt run --project-dir transform --profiles-dir transform

test:
	dbt test --project-dir transform --profiles-dir transform

dbt-docs:
	dbt docs generate --project-dir transform --profiles-dir transform
	dbt docs serve --project-dir transform --profiles-dir transform

# --- app ---
dashboard:
	streamlit run dashboard/app.py

# --- everything, from a cold start ---
all: up pipeline build test
