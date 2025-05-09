#!/usr/bin/env python
"""webapp.py: makes webapp apps (http://webpy.org)"""



__version__ = "0.37"
__author__ = [
    "Aaron Swartz <me@aaronsw.com>",
    "Anand Chitipothu <anandology@gmail.com>"
]
__license__ = "public domain"
__contributors__ = "see http://webpy.org/changes"

# server/webapp/__init__.py

from . import webapi
from . import db
from .application import application

# Re-export required webapi symbols for compatibility
ctx = webapi.ctx
storage = webapi.storage
header = webapi.header
badrequest = webapi.badrequest
notfound = webapi.notfound
internalerror = webapi.internalerror

# Expose the database interface
database = db.base.database
