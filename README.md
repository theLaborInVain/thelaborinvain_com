# https://thelaborinvain.com
The home/index website for The Labor in Vain, a production company from Chicago, IL.

The blog application (under /blog) is based on
[Miguel Grinberg's Microblog](https://blog.miguelgrinberg.com).


## Install and deploy the blog
1. get-clone the repo
1. cd into the blog root, e.g. `thelaborinvain_com/blog` 
1. install the virtual environment: `python3 -m venv venv`
1. activate the virtual environment: `source venv/bin/activate`
1. install requires: `pip install -r requirements.txt`

At this point, you should be able to start the server in dev mode: `./server.sh dev`

If you want to actually deploy the blog, do this:

1. create a symlink to the Nginx config file in `deploy`, e.g. something like this:

	ln -s /home/toconnell/thelaborinvain_com/deploy/nginx.conf /etc/nginx/sites-enabled/blog_thelaborinvain_com

1. do the same thing for the Supervisor config file:

	ln -s /home/toconnell/thelaborinvain_com/deploy/supervisor.conf /etc/supervisor/conf.d/thelaborinvain_blog

1. reload Nginx and Supervisor and you should be good to go!
