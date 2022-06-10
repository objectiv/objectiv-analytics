requirements:
	pip install -r requirements.txt

isort:
	isort .

pycodestyle:
	pycodestyle checklock_holmes

mypy:
	mypy checklock_holmes

check-dev: requirements isort pycodestyle mypy

checklock-inspection:
	python main.py --engine=all

checklock-inspection-bigquery:
	python main.py --engine=bigquery
