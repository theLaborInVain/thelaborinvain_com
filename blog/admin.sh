#!/bin/bash

#
#   Use this to run the server in dev mode, e.g. from the CLI.
#   DO NOT use this script for deployment: all of that happens in the
#   'deploy' folder off of the project root.
#

PROJECT_ROOT=/home/toconnell/thelaborinvain_com/blog

[ ! `pwd` == $PROJECT_ROOT ] && {
    echo -e "Please run from the project root!\n$PROJECT_ROOT";
    exit 2; 
}

source venv/bin/activate
export PYTHONPATH="`pwd`"

PYTHON_PATH=`which python`
PYTHON_VERS=`python --version`
echo -e " * interpreter: $PYTHON_PATH ($PYTHON_VERS)"
echo -e " *  PYTHONPATH: $PYTHONPATH"

python $PROJECT_ROOT/app/admin $@
