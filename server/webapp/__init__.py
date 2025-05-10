# server/webapp/__init__.py

print("✅ server.webapp.__init__.py loaded", flush=True)

#!/usr/bin/env python
"""webapp: adapted from original web.py clone."""

from . import utils, net, wsgi, web_http as http, webapi, httpserver, debugerror
from . import template, form, session, application, browser

from .utils import *
from .net import *
from .wsgi import *
from .web_http import *
from .webapi import *
from .httpserver import *
from .debugerror import *
from .application import *
from .browser import *
from .utils import storage

try:
    import webopenid as openid
except ImportError:
    pass  # requires openid module

from server.database import database, select, query, insert, transaction
