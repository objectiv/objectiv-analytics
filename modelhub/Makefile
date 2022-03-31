.PHONY: tests

tests:
	mypy modelhub
	pycodestyle modelhub
	pytest tests_modelhub -W error::DeprecationWarning
