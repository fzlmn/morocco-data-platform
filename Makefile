.PHONY: up down reset install pipeline dashboard

up:
	docker compose up -d

down:
	docker compose down

reset:
	docker compose down -v && docker compose up -d

install:
	pip install -r requirements.txt

pipeline:
	python -m extract.run && python -m load.run

dashboard:
	streamlit run dashboard/app.py
