ifdef OS
	SEP := ;
else
  	SEP := :
endif

docker-build:
	docker build -t gimme-aws-creds .

test: docker-build
	pytest -vv tests
