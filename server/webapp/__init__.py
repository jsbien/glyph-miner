# server/webapp/__init__.py

print("✅ server.webapp.__init__.py loaded", flush=True)

from .webapi import *
from .db import database


# Optional: expose the webapi module itself if needed elsewhere
# import server.webapp.webapi as webapi
