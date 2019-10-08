#!/bin/bash

#
#   based on what we did for the admin.sh in the kdm-manager.api project
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
