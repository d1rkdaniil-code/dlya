.PHONY: run test lint clean

run:
	FLASK_ENV=development python -m flask run

test:
	pytest -v

lint:
	flake8 app tests
	mypy app

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	rm -rf .pytest_cache .mypy_cache