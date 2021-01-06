init:
	pip3.8 install -r requirements.txt
devel:
	pip3.8 install -r requirements_dev.txt
	pre-commit install
test:
	tox
lint:
	flake8 pyetrade tests
install:
	pip3.8 install --upgrade .
dist:
	python setup.py sdist
clean:
	find . -iname *.pyc -exec rm -f {} +
	pip3.8  uninstall -y pyetrade
