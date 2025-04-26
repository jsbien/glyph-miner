# server/web/wsgi.py

from web import application

# URL mappings
urls = (
    '/', 'Index',
)

# A simple handler for the root URL
class Index:
    def GET(self):
        return "Hello, glyph-miner! Server is working."

# Create the WSGI app
app = application(urls, globals()).wsgifunc()
# server/web/wsgi.py

from web import application

urls = (
    '/', 'Index',
)

class Index:
    def GET(self):
        return "Hello, glyph-miner! Server is working."

# Create the WSGI app
app = application(urls, globals()).wsgifunc()
