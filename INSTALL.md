In preparation

# Docker

[![Docker Image Version](https://img.shields.io/docker/v/glyphminer/glyphminer?sort=semver)](https://hub.docker.com/r/glyphminer/glyphminer)
[![Image Size](https://img.shields.io/badge/size-203.6MB-lightgrey)](https://hub.docker.com/r/glyphminer/glyphminer) [![Layers](https://img.shields.io/badge/layers-18-blue)](https://hub.docker.com/r/glyphminer/glyphminer)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)


## on Linux

## on Windows

## Manual Installation
The Glyph Miner software is preferably installed on a Linux
machine. This guide shows how to install the software on GNU/Linux
Debian bookworm (the stable distribution at the moment of this
writing); for other distributions, the process is similar.

### Select appropriate free ports

One port is needed to access the system, we use here 9090. Another one
is used for the internal communication between the system components,
we use for this purpose  9091. Both can be changes, see below.

### Required Packages
First, make sure you have the following packages installed on your system:

`nginx mysql-server git python-numpy python-pil make g++ python-dev python-pip python-mysqldb`

For Debian bookworm this means:

* nginx/stable,now 1.22.1-9+deb12u1 amd64 [installed]
  * nginx-common/stable,now 1.22.1-9+deb12u1 all [installed,automatic]
* python3-numpy/stable,now 1:1.24.2-1+deb12u1 amd64 [installed,automatic]
* default-mysql-server:
  * mariadb-server/stable,now 1:10.11.11-0+deb12u1 amd64 [installed]
     * mariadb-server-core/stable,now 1:10.11.11-0+deb12u1 amd64 [installed,automatic]
* g++/stable,now 4:12.2.0-3 amd64 [installed]
  * g++-12/stable,now 12.2.0-14 amd64 [installed,automatic]
* git/stable,stable-security,now 1:2.39.5-0+deb12u2 amd64 [installed]
* python3-pil/stable,stable-security,now 9.4.0-1.1+deb12u1 amd64 [installed]
  * python3-pil.imagetk/stable,stable-security,now 9.4.0-1.1+deb12u1 amd64 [installed,automatic]
* python3-dev/stable,now 3.11.2-1+b1 amd64 [installed,automatic]
  * libpython3-dev/stable,now 3.11.2-1+b1 amd64 [installed,automatic]
* python3-pip/stable,now 23.0.1+dfsg-1 all [installed]
  * python3-pip-whl/stable,now 23.0.1+dfsg-1 all [installed,automatic]
* python3-mysqldb/stable,now 1.4.6-2+b1 amd64 [installed]


### Other prerequisites

Install uWSGI (now version 3.11.2) in a virtual environment:


	python3 -m venv --system-site-packages ~/glyph-miner/git/glyph-miner/uwsgi-env
	source ~/git/glyph-miner/uwsgi-env/bin/activate
	sudo pip install uwsgi`

### Obtaining  Glyph Miner
Clone the git repository:

	
	git clone https://github.com/jsbien/glyph-miner.git

Make sure the correct rights are set so that the server can
write into `web/tiles`, `web/thumbnails`, `web/synthetic_pages`, `server/images`
and `server/templates`. Use `chmod` or `chown` if needed.



### Compiling binaries


Next compile the C++ library that handles the template matching:

    cd glyph-miner/server
    make standalone


### Setting up nginx and uWSGI
The python server (handling the image processing and the connection to the
database) will be accessible through an nginx web server (handling the static
content).

Let nginx know that calls to the API will be handled by the python server by
copying the `local/default` file to /etc/nginx/sites-enabled/default.

Its content is given below:

	server {
    listen 9090 default_server;
    listen [::]:9090 default_server;

    root /home/jsbien/git/glyph-miner/web;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location /api/ {
        include uwsgi_params;
        uwsgi_pass 127.0.0.1:9091;
        uwsgi_read_timeout 300;
        client_max_body_size 100M;
    }
	}

> Modify the paths to root appropriately!


If needed or desired, change the port(s) in `listen` and `uwsgi_pass`,
and possibly in `local/run-uwsgi.sh` mentioned later.

Do not forget to restart nginx in order to make your changes work:
`sudo service nginx restart`

> Be aware that this change affects the entire nginx setup!

### Setting up the database
Glyph Miner uses a MySQLcompatible MariaDB database to store its
data.

Create a new database and user `glyphminer` for Glyph Miner
using `init_glyphminer_db.sql`:

	mysql -u root -p < local/init_glyphminer_db.sql

> Note that you have to run this as the root user (or any user with
CREATE USER privilege)!

Than import the database structure into the new database:

	mysql -u glyphminer -pglyphminer < server/schema.sql

You can configure the credentials that Glyph Miner will use in `server/server.py`,
line 25.

For the debugging purposes it may be useful to access logs ...

### Starting it up

Start the server with the `local/run-uwsgi.sh` script to run uwsgi
with timestamped log capturing print() and erroroutput.  This is its
main content:

exec /home/jsbien/git/glyph-miner/uwsgi-env/bin/uwsgi \
  --socket 127.0.0.1:9091 \
  --protocol uwsgi \
  --chdir /home/jsbien/git/glyph-miner \
  --pythonpath /home/jsbien/git/glyph-miner \
  --module server.server:application \
  --master \
  --processes 1 \
  --threads 2 \
  --logto uwsgi-$(date +%Y%m%d-%H%M%S).log

> Modify the paths appropriately!

You can also (re)start server with `local/restart-server.sh` or
`local/run-uwsgi.sh`. In both cases you can kill the server cleanly
with `kill-uwsgi.sh` (for this purpose the PID is stored in
`/tmp/uwsgi-wrapper.pid`).

To validate server startup use one of the testing tools described
below.

### Testing

Various testing tools are available in the `local/` directory.

#### Regressions testing

The primary tool is `local/full-check.sh`. 

#### Database testing

You can test the database with the commands like this:

	mysql -u glyphminer -pglyphminer -e 'SHOW TABLES FROM glyphminer'

#### 🔧 Development Server with Interactive Debugging

To run the server with live code reloading and a browser-based debugger, use:

$ python3 utils/debug_wsgi_runner.py

This starts the server on http://localhost:9099.

- When an error occurs, you’ll see an interactive traceback in the browser.
- You can click into stack frames to inspect variables and evaluate expressions.

> ⚠  Do not use this in production — it's for local development and debugging only.


### User utilities

The directory `utils/` is dedicated for user-oriented utilities.

At the moment only `batch_upload_pages.py` is provided (not yet
working!).
