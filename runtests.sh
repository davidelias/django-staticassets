#!/bin/bash

set -e

export PYTHONPATH=$PWD:$PWD/..:$PYTHONPATH

django-admin.py test --settings=tests.settings -v 2
