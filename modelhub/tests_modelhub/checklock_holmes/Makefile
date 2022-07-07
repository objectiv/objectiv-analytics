install_env_bach:
	pip install -e ../../../bach

install_env_modelhub:
	pip install -e ../../../modelhub

requirements:
	pip install -r requirements.txt

requirements-env: requirements install_env_bach install_env_modelhub

isort:
	isort .

pycodestyle:
	pycodestyle checklock_holmes

mypy:
	mypy checklock-holmes.py checklock_holmes

check-dev: requirements isort pycodestyle mypy

checklock-inspection:
	python checklock-holmes.py --engine=all

checklock-inspection-bigquery:
	python checklock-holmes.py --engine=bigquery
