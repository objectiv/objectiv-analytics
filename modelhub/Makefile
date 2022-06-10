.PHONY: tests

tests:
	mypy modelhub
	pycodestyle modelhub
	pytest -n 4 --dist loadgroup tests_modelhub/unit tests_modelhub/functional tests_modelhub

tests-bigquery:
# Similar to `tests`, but tests that can run against multiple databases will be run against BigQuery instead
# of Postgres. Note that most of our test-suite is postgres-only. The postgres-only tests will still run
# against Postgres
	mypy modelhub
	pycodestyle modelhub
	pytest --all -n 8 --dist loadgroup --big-query tests_modelhub


tests-all:
# Similar to `tests`, but tests that can run against multiple databases will be run against both BigQuery
# and Postgres. Note that most of our test-suite is postgres-only. The postgres-only tests will still only
# run against Postgres
	mypy modelhub
	pycodestyle modelhub
	pytest --all -n 8 --dist loadgroup tests_modelhub
