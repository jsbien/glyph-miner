# coding: utf-8
from server.webapp.application import application
import json

# Dummy handlers
def get_collections():
    return [
        '200 OK',
        [('Content-Type', 'application/json')],
        [json.dumps([]).encode('utf-8')]
    ]

def get_images():
    return [
        '200 OK',
        [('Content-Type', 'application/json')],
        [json.dumps([]).encode('utf-8')]
    ]

def get_glyphs():
    return [
        '200 OK',
        [('Content-Type', 'application/json')],
        [json.dumps([]).encode('utf-8')]
    ]

def get_pages():
    return [
        '200 OK',
        [('Content-Type', 'application/json')],
        [json.dumps([]).encode('utf-8')]
    ]

def get_documents():
    return [
        '200 OK',
        [('Content-Type', 'application/json')],
        [json.dumps([]).encode('utf-8')]
    ]

# URL routing
urls = (
    '/collections', get_collections,
    '/images', get_images,
    '/glyphs', get_glyphs,
    '/pages', get_pages,
    '/documents', get_documents,
)

# Build WSGI app
app = application(urls, globals()).wsgifunc()
