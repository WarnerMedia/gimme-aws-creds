ifdef OS
	BIN    := Scripts
	PYTHON := python
	SEP := ;
	SFX := .cmd
else
	BIN    := bin
	PYTHON := python3
	SEP := :
	SFX :=
endif

docker-build:
	docker build -t gimme-aws-creds .

test: docker-build
	pytest -vv tests

venv:
	$(PYTHON) -mvenv ./venv

init:	venv
	./venv/$(BIN)/$(PYTHON) -mpip install -r requirements_dev.txt

exe: init
	./venv/$(BIN)/$(PYTHON) -mpip install .
	$(eval FIDODIR := $(shell ./venv/$(BIN)/$(PYTHON) -c "import fido2;from os import path as op;print(op.dirname(fido2.__file__))"))
	./venv/$(BIN)/$(PYTHON) -mPyInstaller -F --hidden-import=gimme_aws_creds --add-data "$(FIDODIR)/public_suffix_list.dat$(SEP)fido2" bin/gimme-aws-creds

clean:
	rm -rf build dist venv 
