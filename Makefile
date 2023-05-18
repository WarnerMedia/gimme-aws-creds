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
	nosetests -vv tests

venv:
	$(PYTHON) -mvenv ./venv

init:	venv
	./venv/bin/$(PYTHON) -mpip install -r requirements_dev.txt


exe: init
	./venv/bin/$(PYTHON) -mpip install .
	$(eval FIDODIR := $(shell ./venv/bin/python3 -c "import fido2;from os import path as op;print(op.dirname(fido2.__file__))"))
	./venv/bin/$(PYTHON) -mPyInstaller -F --hidden-import=gimme_aws_creds --add-data "$(FIDODIR)/public_suffix_list.dat$(SEP)fido2" bin/gimme-aws-creds
