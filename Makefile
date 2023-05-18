ifdef OS
	SEP := ;
else
  	SEP := :
endif

init:
	python3 -mpip install -r requirements_dev.txt

docker-build:
	docker build -t gimme-aws-creds .

test: docker-build
	nosetests -vv tests

exe: init
	python3 -mpip install .
	$(eval FIDODIR := $(shell python3 -c "import fido2;from os import path as op;print(op.dirname(fido2.__file__))"))
	pyinstaller -F --hidden-import=gimme_aws_creds --add-data "$(FIDODIR)/public_suffix_list.dat$(SEP)fido2" bin/gimme-aws-creds
