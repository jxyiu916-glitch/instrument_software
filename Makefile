install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

test:
	. .venv/bin/activate && pytest -q

run-example:
	python -m src.cli data/example_small.json

lint:
	mypy src tests || true
