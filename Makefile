ifdef OS
	PYTHON := python
	SEP := ;
else
	PYTHON := python3
	SEP := :
endif

docker-build:
	docker build -t gimme-aws-creds .

test: docker-build
	pytest -vv tests
