install:
	python -m pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

ingest:
	python scripts/ingest_documents.py

test:
	pytest -q

up:
	docker compose up -d --build

down:
	docker compose down
