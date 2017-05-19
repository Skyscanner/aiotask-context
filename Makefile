syntax:
	flake8 --exclude=examples/

cov:
	pytest --cov-report term-missing --cov=aiotask_context -sv tests/test_context.py
