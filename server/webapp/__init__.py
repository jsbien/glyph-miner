# server/webapp/__init__.py

print("✅ server.webapp.__init__.py loaded", flush=True)

# from .webapi import *
# from server.webapp import web
# from .db import database
from server.database import database

from . import web

# Sanity check: ensure we're importing the correct module and application is callable
if hasattr(web, 'application') and callable(web.application):
    print("✅ server.webapp.web.application is callable")
else:
    print("❌ ERROR: server.webapp.web.application is missing or not callable")

# Optional: expose the webapi module itself if needed elsewhere
# import server.webapp.webapi as webapi
