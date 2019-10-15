#!/bin/bash

pushd /home/toconnell/thelaborinvain_com/blog
source venv/bin/activate
export FLASK_ENV=production
venv/bin/gunicorn -b localhost:8060 -w 4 app:app
