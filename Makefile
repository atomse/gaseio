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
	bash -c 'unset PYTHONPATH; pipreqs --force $(Project)'
	mv $(Project)/requirements.txt .
	bash -c '[ "$(shell uname)" == "Darwin" ] && sed -i "" "s/==/>=/g" requirements.txt || sed -i "s/==/>=/g" requirements.txt'
	bash -c '[ "$(shell uname)" == "Darwin" ] && sed -i "" "s/numpy.*/numpy/g" requirements.txt || sed -i "s/numpy.*/numpy/g" requirements.txt'
	bash -c '[ "$(shell uname)" == "Darwin" ] && sed -i "" "s/psutil.*/psutil/g" requirements.txt || sed -i "s/psutil.*/psutil/g" requirements.txt'
	sort requirements.txt -o requirements.txt
	cat requirements.txt 

build:
	rm -rf build/ sdist/ dist/ $(Project)-*/ $(Project).egg-info/
	python setup.py sdist build
	python setup.py bdist_wheel --universal
	twine check dist/*

install:
	cd /tmp; pip uninstall -yy $(Project); cd -; python setup.py install || python setup.py install --user

test:
	bash -c "export PYTHONPATH="$(PYTHONPATH):$(pes_parent_dir)"; export GASEIO_CONTINUE_FILE="$(GASEIO_CONTINUE_FILE)"; coverage run --source $(Project) ./tests/test.py" 
	echo `which $(Project)`
	# coverage run --source $(Project) `which $(Project)` -h
	# coverage run --source $(Project) `which $(Project)` LISTSUBCOMMAND
	# coverage run --source $(Project) `which $(Project)` LISTSUBCOMMAND | xargs -n 1 -I [] bash -c '(coverage run --source $(Project) `which $(Project)` [] -h >/dev/null 2>&1 || echo ERROR: [])'
	# coverage report -m
	coverage report -m > coverage.log
	cat coverage.log


test_app:
	bash -c "export GASEIO_PORT=5001; export PYTHONPATH=$(pes_parent_dir):$(PYTHONPATH); python -m gaseio.app"


test_server:
	bash -c "export GASEIO_PORT=5001; export PYTHONPATH=$(pes_parent_dir):$(PYTHONPATH); python -m gaseio.server"


test_chemio:
	make test_chemio_info
	make test_chemio_convert
	echo read error
	cat /tmp/testresult
	echo 
	echo write error
	cat /tmp/testfiletype


test_chemio_info:
	rm -rf /tmp/gaseio_testresult
	export CHEMIO_SERVER_URLS=http://localhost:5000/; \
	for filename in tests/Testcases/*.*; \
	do \
		[ -f $$filename ] && chemio info $$filename || echo $$filename >> /tmp/gaseio_testresult; \
	done;
	echo read error
	cat /tmp/gaseio_testresult


test_chemio_convert:
	rm -rf /tmp/gaseio_testfiletype
	export CHEMIO_SERVER_URLS=http://localhost:5000/; \
	for filetype in `python -c 'import gaseio; print(gaseio.list_supported_write_formats("string"))'`; \
	do \
		chemio convert  tests/Testcases/test.xyz - -o $$filetype || echo $$filetype >> /tmp/gaseio_testfiletype; \
	done;
	echo write error
	cat /tmp/gaseio_testfiletype


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
