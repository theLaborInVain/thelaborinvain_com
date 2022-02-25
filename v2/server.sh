#!/bin/bash

# path to self
SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

start_venv() {

    # change to the directory where server.sh lives
    pushd $SCRIPTPATH > /dev/null

   # sanity check: log the launch time; make the log dir if it doesn't exist
    LAUNCHTIME=`date +%F' '%T`
    echo -e "[$LAUNCHTIME] Starting development server..."

    source $SCRIPTPATH/venv/bin/activate

    export FLASK_ENV=dev
    export FLASK_DEBUG=1
    export FLASK_RUN_PORT=9999
    export FLASK_RUN_HOST='0.0.0.0'

    echo -e "\nPIP:"
    pip freeze $1 | while read x; do echo -e " * $x"; done
    echo -e
    echo -e "Flask server:"

}

start_venv
flask run
