#!/usr/bin/env python3
# encoding: utf-8
"""
application.py
Updated: 2025-05-10
Fix: Import proper webapi exceptions and use them in try/except blocks to avoid TypeError.
Fix: Import correct exception classes (Redirect, _NotFound) from webapi to avoid TypeErrors when catching.
Fix TypeError by ensuring handler is class before instantiation
"""

import sys
import re
import types
import traceback
import server.webapp as web
from server.webapp.webapi import _NotFound, Redirect  # ✅ Correct exception classes

class application:
    def __init__(self, mapping, fvars):
        self.mapping = mapping  # will be replaced by resolve_route()
        self.fvars = fvars
        self.args = []

    def resolve_route(self, path):
        print(f"[DEBUG] resolve_route() called with path: {path}")
        print(f"[DEBUG] self.mapping = {self.mapping} (type: {type(self.mapping)}, len: {len(self.mapping)})")
        """Match the path against self.mapping and return (handler_key, args)."""
        for i in range(0, len(self.mapping), 2):
            regex, handler_key = self.mapping[i], self.mapping[i + 1]
            match = re.compile("^" + regex + "$").match(path)
            if match:
                return handler_key, list(match.groups())
        return None, []

    def wsgifunc(self):
        def wsgi(env, start_resp):
            web.ctx = web.storage()
            web.ctx.headers = []
            web.ctx.env = env
            web.ctx.path = env.get('PATH_INFO', '/')
            web.ctx.fullpath = web.ctx.path
            web.ctx.method = env.get('REQUEST_METHOD', 'GET')

            handler_key, args = self.resolve_route(web.ctx.path)

            try:
                result = self.handle_with_processors()

                if not isinstance(result, (str, bytes, list, tuple)):
                    raise TypeError(f"Invalid response type: {type(result)}, value: {result}")

                if isinstance(result, list):
                    status = '200 OK'
                    headers = [('Content-Type', 'text/html')] + web.ctx.headers
                    start_resp(status, headers)
                    return result
                elif isinstance(result, str):
                    start_resp('200 OK', [('Content-Type', 'text/html')])
                    return [result.encode('utf-8')]
                elif isinstance(result, bytes):
                    start_resp('200 OK', [('Content-Type', 'text/html')])
                    return [result]

                start_resp('500 Internal Server Error', [('Content-Type', 'text/plain')])
                return [b"Internal Server Error"]

            except (_NotFound, Redirect):
                raise
            except Exception:
                print(traceback.format_exc())
                start_resp('500 Internal Server Error', [('Content-Type', 'text/plain')])
                return [b"Internal Server Error"]

        return wsgi

    def handle_with_processors(self):
        try:
            handler_key, args = self.resolve_route(web.ctx.path)
            return self._delegate(handler_key, self.fvars, args)
        except _NotFound:
            raise
        except Exception:
            print(traceback.format_exc())
            raise

    def _delegate(self, f, fvars, args=[]):
        def handle_class(cls):
            if not isinstance(cls, type):
                raise TypeError(f"Expected class, got instance of {type(cls).__name__}")
            meth = web.ctx.method
            if meth == 'HEAD' and not hasattr(cls, meth):
                meth = 'GET'
            if not hasattr(cls, meth):
                raise web.nomethod(cls)
            tocall = getattr(cls(), meth)
            return tocall(*args)

        def is_class(o):
            return isinstance(o, type)

        if f is None:
            raise web.notfound()
        elif isinstance(f, application):
            return f.handle_with_processors()
        elif isinstance(f, type):
            return handle_class(f)
        elif hasattr(f, '__call__'):
            return f(*args)
        else:
            raise web.notfound()
        elif isinstance(f, str):
            if f.startswith('redirect '):
                url = f.split(' ', 1)[1]
                if web.ctx.method == "GET":
                    x = web.ctx.env.get('QUERY_STRING', '')
                    if x:
                        url += '?' + x
                raise web.redirect(url)
            elif '.' in f:
                mod, cls = f.rsplit('.', 1)
                mod = __import__(mod, None, None, [''])
                cls = getattr(mod, cls)
            else:
                print(f"[DEBUG] _delegate f = {f}, fvars keys = {list(fvars.keys())}", flush=True)
                cls = fvars[f]
            return handle_class(cls)
        elif hasattr(f, '__call__'):
            return f()
        else:
            raise web.notfound()
