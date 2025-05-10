# server/webapp/__init__.py

print("✅ server.webapp.__init__.py loaded", flush=True)

#!/usr/bin/env python
"""webapp: adapted from original web.py clone."""

import utils, net, wsgi, web_http as http, webapi, httpserver, debugerror
import template, form, session, application, browser

from utils import *
# from db import *
from net import *
from wsgi import *
from web_http import *
from webapi import *
from httpserver import *
from debugerror import *
from application import *
from browser import *

try:
    import webopenid as openid
except ImportError:
    pass  # requires openid module

from server.database import database, select, query, insert, transaction


# from .base import database, register_database
# from .querying import select, query
# from .inserting import insert
# from .transaction import transaction

# __all__ = [
#     "database",
#     "select",
#     "query",
#     "insert",
#     "transaction"
# ]
