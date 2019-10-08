echo -e "\nVirtual Envrionment:"


start_venv() {
    source venv/bin/activate

    export FLASK_ENV=$1

    PYTHON_PATH=`which python`
    PYTHON_VERS=`python --version`
    echo -e " * $PYTHON_PATH"
    echo -e " * Python $PYTHON_VERS"

    echo -e " * FLASK_ENV=$FLASK_ENV"
    echo -e "\nPIP:"
    pip freeze $1 | while read x; do echo -e " * $x"; done
    echo -e
    echo -e "Flask server:"

}

#
#   Process CLI args
#

case "$1" in
    dev)
        start_venv development
        python blog.py
        ;;
    *)
        echo "Usage: $NAME {dev|prod}" >&2
        exit 3
esac
