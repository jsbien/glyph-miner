#!/usr/bin/env python3
# server/server.py

import os
import sys

# setup the correct path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from server import webapp
from server import pagecreator

# --- URL mappings ---
urls = (
    '/', 'server',
    '/load', 'loader',
    '/save', 'saver',
    '/upload', 'uploader',
    '/add', 'adder',
    '/remove', 'remover',
)

app = webapp.application(urls, globals())
application = app.wsgifunc() 

# --- Handlers ---
class server:
    def GET(self):
        print("[DEBUG] server.GET() called")
        try:
            with open('/opt/glyph-miner/web/index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            print("[DEBUG] index.html loaded successfully, length:", len(content))
            return [content.encode('utf-8')]  # WSGI expects iterable of bytes
        except Exception as e:
            print("[ERROR] Failed to load index.html:", e)
            return [("Error loading index.html: " + str(e)).encode('utf-8')]

class loader:
    def POST(self):
        # (Dummy placeholder)
        return "Loader not implemented yet."

class saver:
    def POST(self):
        # (Dummy placeholder)
        return "Saver not implemented yet."

class uploader:
    def POST(self):
        # (Dummy placeholder)
        return "Uploader not implemented yet."

class adder:
    def POST(self):
        # (Dummy placeholder)
        return "Adder not implemented yet."

class remover:
    def POST(self):
        # (Dummy placeholder)
        return "Remover not implemented yet."

# --- Manual WSGI server ---
if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    print("Serving Glyph Miner on http://0.0.0.0:8081")
    httpd = make_server('', 8081, app)
    httpd.serve_forever()
