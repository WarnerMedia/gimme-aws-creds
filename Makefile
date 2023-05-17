ifdef OS
	SEP := ;
else
  	SEP := :
endif

init:
	python -mpip install -r requirements_dev.txt

docker-build:
	docker build -t gimme-aws-creds .

test: docker-build
	pytest -vv tests
