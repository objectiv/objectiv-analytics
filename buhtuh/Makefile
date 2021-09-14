.PHONY: tests

tests:
	mypy buhtuh sql_models
	pycodestyle --max-line-length=110 buhtuh sql_models
	pytest tests/
