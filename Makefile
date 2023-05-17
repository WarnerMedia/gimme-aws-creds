ifdef OS
	SEP := ;
	SFX := .cmd
else
  SEP := :
	SFX :=
endif
FIDODIR := $(shell python -c "import fido2;from os import path as op;print(op.dirname(fido2.__file__))")

init:
	pip3 install -r requirements_dev.txt

docker-build:
	docker build -t gimme-aws-creds .

test: docker-build
	pytest -vv tests
