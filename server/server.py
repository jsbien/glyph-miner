from server import webapp  # <- Correct import!

from server.glyphs import Glyphs
from server.collections import Collections

# URL mapping
urls = [
    ('/glyphs', Glyphs),
    ('/collections', Collections),
]

# Create the application
app = webapp.application(urls, globals())
application = app.wsgifunc()
