#!/usr/bin/env bash

cd $(cd `dirname $0` && pwd)
cd ..

source venv/bin/python
export PYTHONPATH=`pwd`
cd tests
python -m unittest discover .
