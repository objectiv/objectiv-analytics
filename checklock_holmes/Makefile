requirements:
	pip install -r requirements.txt

isort:
	isort .

pycodestyle:
	pycodestyle checklock_holmes

mypy:
	mypy checklock_holmes

check: requirements isort pycodestyle mypy
