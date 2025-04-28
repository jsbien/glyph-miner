# coding: utf-8
from server.webapp.application import application
import json

# Handler class for /collections
class CollectionsHandler:
    def GET(self):
        # Return an empty list of collections (initial state)
        return [
            '200 OK',
            [('Content-Type', 'application/json')],
            [json.dumps([]).encode('utf-8')]
        ]

    def POST(self):
        # Dummy collection created, normally you would process posted data
        dummy_collection = {
            "id": 1,
            "name": "New Collection",
            "description": "",
            "documents": []
        }
        return [
            '201 Created',
            [('Content-Type', 'application/json')],
            [json.dumps(dummy_collection).encode('utf-8')]
        ]

# Define the URL mappings
urls = [
    ('/collections', CollectionsHandler),
]

# Build the WSGI application
app = application(urls, globals()).wsgifunc()
