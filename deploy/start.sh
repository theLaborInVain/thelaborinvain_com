#!/bin/bash

pushd /home/toconnell/thelaborinvain_com/blog
source venv/bin/activate
export FLASK_ENV=production
export SECRET_KEY=5da751b25ad39e517b79b940
venv/bin/gunicorn -b localhost:8060 -w 4 app:app 
#venv/bin/gunicorn -b 0.0.0.0:8060 -w 4 app:app
