## Docker

# on Linux

# on Windows

## Manual Installation
The Glyph Miner software is preferably installed on a Linux
machine. This guide shows how to install the software on GNU/Linux
Debian bookworm (the stable distribution at the moment of this
writing); for other distributions, the process is similar.

### Required Packages
First, make sure you have the following packages installed on your system:

`nginx mysql-server git python-numpy python-pil make g++ python-dev python-pip python-mysqldb`

* nginx/stable,now 1.22.1-9+deb12u1 amd64 [installed]
  * nginx-common/stable,now 1.22.1-9+deb12u1 all [installed,automatic]
* python3-numpy/stable,now 1:1.24.2-1+deb12u1 amd64 [installed,automatic]
* default-mysql-server:
  * mariadb-server/stable,now 1:10.11.11-0+deb12u1 amd64 [installed]
     * mariadb-server-core/stable,now 1:10.11.11-0+deb12u1 amd64 [installed,automatic]
* g++/stable,now 4:12.2.0-3 amd64 [installed]
  * g++-12/stable,now 12.2.0-14 amd64 [installed,automatic]
* git/stable,stable-security,now 1:2.39.5-0+deb12u2 amd64 [installed]
* python3-pil: Installed: 9.4.0-1.1+deb12u1 ???
* python3-dev: Installed: 3.11.2-1+b1 ???
* python3-pip: Installed: 23.0.1+dfsg-1 ???
* python3-mysqldb/stable,now 1.4.6-2+b1 amd64 [installed]


### Other prerequisites

Install uWSGI (now version 3.11.2) in a virtual environment:


	python3 -m venv --system-site-packages ~/glyph-miner/git/glyph-miner/uwsgi-env
	source ~/git/glyph-miner/uwsgi-env/bin/activate
	sudo pip install uwsgi`

### Obtaining  Glyph Miner
To get the latest version of the software, clone the git repository:
`git clone https://github.com/benedikt-budig/glyph-miner.git`

### Compiling binaries


Next, you need to compile the C++ library that handles the template matching:


    cd glyph-miner/server
    make standalone

Last but not least, make sure the correct rights are set so that the server can
write into `web/tiles`, `web/thumbnails`, `web/synthetic_pages`, `server/images`
and `server/templates`.


### Setting up nginx and uWSGI
The python server (handling the image processing and the connection to the
database) will be accessible through an nginx web server (handling the static
content).

Let nginx know that calls to the API will be handled by the python server by
adding the following lines in /etc/nginx/sites-enabled/default:

    root    /home/<username>/glyph-miner/web

    location /api/ {
        root /home/<username>/glyph-miner/server;
        client_max_body_size 100M;

        include uwsgi_params;
        uwsgi_pass 127.0.0.1:9090;
        uwsgi_read_timeout 300;
    }

Do not forget to restart nginx in order to make your changes work:
`sudo service nginx restart`


### Setting up the database
Glyph Miner uses a MySQL database to store its data. Create a new database and
user `glyphminer` for Glyph Miner:

    mysql -u root -p
    mysql> create database glyphminer;
    mysql> grant usage on *.* to glyphminer@localhost identified by 'glyphminer';
    mysql> grant all privileges on glyphminer.* to glyphminer@localhost;

Import the database structure into the new database:

    mysql -u glyphminer -p glyphminer < server/schema.sql

You can configure the credentials that Glyph Miner will use in `server/server.py`,
line 49.

Run as MySQL root user (or any user with CREATE USER privilege):
mysql -u root -p < local/init_glyphminer_db.sql
Run as MySQL root user (or any user with CREATE USER privilege):
mysql -u glyphminer -pglyphminer < server/schema.sql


### Starting it up
You can start the python server using uwsgi using the following command:

`/usr/local/bin/uwsgi --socket 127.0.0.1:9090 --chdir /home/<username>/glyph-miner/server/ --wsgi-file /home/<username>/glyph-miner/server/server.py --master --processes 4 --threads 2`

local/run-uwsgi.sh

### Testing

local/debug_wsgi_runner.py
