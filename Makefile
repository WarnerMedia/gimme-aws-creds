init:
	pip3 install -r requirements_dev.txt

docker-build:
	docker build -t gimme-aws-creds .

test: docker-build
	nosetests -vv tests

dist/gimme-aws-creds:
	pip3 install -r requirements.txt
	pip3 install pyinstaller
	pyinstaller -p . -F bin/gimme-aws-creds --add-data="$$(python -c 'import fido2, os; print(os.path.dirname(fido2.__file__))'):fido2"


