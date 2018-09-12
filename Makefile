syntax:
	flake8 --exclude=examples/,.tox,.eggs

cov:
	pytest --cov-report term-missing --cov=aiotask_context -sv tests/test_context.py

test:
	pytest tests/ -sv
