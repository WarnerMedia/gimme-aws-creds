init:
	python3 -mpip install -r requirements_dev.txt

docker-build:
	docker build -t gimme-aws-creds .

test: docker-build
	nosetests -vv tests

dist/gimme-aws-creds:
	python3 -mpip install -r requirements.txt
	python3 -mpip install pyinstaller
	pyinstaller -p . -F bin/gimme-aws-creds --add-data="$$(python3 -c 'import fido2, os; print(os.path.dirname(fido2.__file__))'):fido2"


