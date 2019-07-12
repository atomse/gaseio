.PHONY: all reqs build install test

pes_parent_dir:=$(shell pwd)/$(lastword $(MAKEFILE_LIST))
pes_parent_dir:=$(shell dirname $(pes_parent_dir))

Project=$(shell basename $(pes_parent_dir))
GASEIO_CONTINUE_FILE=/tmp/gaseio_continue_file


all:
	make reqs
	make build
	make install
	make test

reqs:
	pipreqs --help >/dev/null 2>&1 || pip3 install pipreqs || pip3 install pipreqs --user
	pipreqs --force $(Project)
	mv $(Project)/requirements.txt .
	bash -c '[ "$(shell uname)" == "Darwin" ] && sed -i "" "s/==/>=/g" requirements.txt || sed -i "s/==/>=/g" requirements.txt'
	bash -c '[ "$(shell uname)" == "Darwin" ] && sed -i "" "s/numpy.*/numpy/g" requirements.txt || sed -i "s/numpy.*/numpy/g" requirements.txt'
	bash -c '[ "$(shell uname)" == "Darwin" ] && sed -i "" "s/psutil.*/psutil/g" requirements.txt || sed -i "s/psutil.*/psutil/g" requirements.txt'
	cat requirements.txt 

build:
	rm -rf build/ sdist/ dist/ $(Project)-*/ $(Project).egg-info/
	python setup.py sdist build
	python setup.py bdist_wheel --universal
	twine check dist/*

install:
	cd /tmp; pip uninstall -yy $(Project); cd -; python setup.py install || python setup.py install --user

test:
	bash -c "export PYTHONPATH="$(PYTHONPATH):$(PWD)"; export GASEIO_CONTINUE_FILE="$(GASEIO_CONTINUE_FILE)"; coverage run --source $(Project) ./tests/test.py" 
	echo `which $(Project)`
	# coverage run --source $(Project) `which $(Project)` -h
	# coverage run --source $(Project) `which $(Project)` LISTSUBCOMMAND
	# coverage run --source $(Project) `which $(Project)` LISTSUBCOMMAND | xargs -n 1 -I [] bash -c '(coverage run --source $(Project) `which $(Project)` [] -h >/dev/null 2>&1 || echo ERROR: [])'
	coverage report -m

test_env:
	bash -c ' \
	rm -rf venv; \
	virtualenv venv; \
	source venv/bin/activate; \
	which python; \
	python --version; \
	pip install -r requirements.txt; \
	make build; \
	make travisinstall; \
	make test'
	
upload:
	echo "\033[41;37m This Project is not allowed to upload to pypi! \033[0m"

clean:
	rm -rf venv build *.egg-info dist
