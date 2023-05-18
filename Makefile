ifdef OS
	SEP := ;
else
  	SEP := :
endif

docker-build:
	docker build -t gimme-aws-creds .

test: docker-build
	nosetests -vv tests

venv:
	python3 -mvenv ./venv

init:	venv
	./venv/bin/python3 -mpip install -r requirements_dev.txt


exe: init
	./venv/bin/python3 -mpip install .
	$(eval FIDODIR := $(shell ./venv/bin/python3 -c "import fido2;from os import path as op;print(op.dirname(fido2.__file__))"))
	./venv/bin/python3 -mPyInstaller -F --paths=.. --hidden-import=gimme_aws_creds --add-data "$(FIDODIR)/public_suffix_list.dat$(SEP)fido2" bin/gimme-aws-creds
