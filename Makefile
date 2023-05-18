ifdef OS
	BIN    := Scripts
	PYTHON := python
	SEP := ;
else
	BIN    := bin
	PYTHON := python3
	SEP := :
endif

docker-build:
	docker build -t gimme-aws-creds .

test: docker-build
	pytest -vv tests
