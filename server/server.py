import webapp  # Import your bundled local web framework (renamed web.py)

# Import your backend handlers
from glyphs import Glyphs
from collections import Collections

# URL mapping
urls = [
    ('/glyphs', Glyphs),
    ('/collections', Collections),
    # (You can later add more routes if needed)
]

# Create the webapp application
app = webapp.application(urls, globals())

# Create the WSGI application for uwsgi
application = app.wsgifunc()
