init:
	pip3 install -r requirements_dev.txt

docker-build:
	docker build -t gimme-aws-creds .

test:
	python -m pip install --upgrade pip -r requirements_dev.txt
	python -m pytest -vv tests
