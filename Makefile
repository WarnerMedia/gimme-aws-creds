init:
	pip3 install -r requirements_dev.txt

docker-build: bin/gimme-aws-creds requirements.txt
	docker build -t gimme-aws-creds .

test: docker-build
	nosetests -vv tests

standalone: init bin/gimme-aws-creds requirements.txt standalone/README.txt
	pyinstaller --collect-all=fido2 --onefile bin/gimme-aws-creds
	cp standalone/README.txt dist
	cd dist && zip gimme-aws-creds.zip *
