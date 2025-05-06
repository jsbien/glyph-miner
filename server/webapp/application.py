import sys
import re
import types
import traceback
import server.webapp.webapi as webapi
from server.webapp.webapi import _NotFound, _Redirect  # Used for isinstance checks

class application:
    def __init__(self, mapping=(), fvars=None):
        self.mapping = mapping
        self.fvars = fvars or {}
        self.args = []

    def resolve_route(self, path):
        """Match the path against self.mapping and return (handler_key, args)."""
        print(f"[DEBUG] resolve_route() called with path: {path}")
        print(f"[DEBUG] self.mapping = {self.mapping} (type: {type(self.mapping)}, len: {len(self.mapping)})")
        for i in range(0, len(self.mapping), 2):
            regex, handler_key = self.mapping[i], self.mapping[i + 1]
            match = re.compile("^" + regex + "$").match(path)
            if match:
                return handler_key, list(match.groups())
        return None, []

    def wsgifunc(self):
        def wsgi(env, start_resp):
            webapi.ctx = webapi.storage()
            webapi.ctx.headers = []
            webapi.ctx.env = env
            webapi.ctx.path = env.get('PATH_INFO', '/')
            webapi.ctx.fullpath = webapi.ctx.path
            webapi.ctx.method = env.get('REQUEST_METHOD', 'GET')

            try:
                result = self.handle_with_processors()

                # Validate and encode response
                if isinstance(result, list):
                    status = '200 OK'
                    headers = [('Content-Type', 'text/html')] + webapi.ctx.headers
                    start_resp(status, headers)
                    return result
                elif isinstance(result, str):
                    start_resp('200 OK', [('Content-Type', 'text/html')])
                    return [result.encode('utf-8')]
                elif isinstance(result, bytes):
                    start_resp('200 OK', [('Content-Type', 'text/html')])
                    return [result]
                else:
                    raise TypeError(f"Invalid response type: {type(result)}, value: {result}")

            except Exception as e:
                # ✅ Let web.py handle known redirects and 404s
                if isinstance(e, (_Redirect, _NotFound)):
                    return e()

                # ❌ Otherwise treat as internal error
                print(traceback.format_exc())
                start_resp('500 Internal Server Error', [('Content-Type', 'text/plain')])
                return [b"Internal Server Error"]

        return wsgi

    def handle_with_processors(self):
        """Main entry point for dispatching request."""
        try:
            handler_key, args = self.resolve_route(webapi.ctx.path)
            return self._delegate(handler_key, self.fvars, args)
        except _NotFound:
            raise
        except Exception:
            print(traceback.format_exc())
            raise

    def _delegate(self, f, fvars, args=[]):
        """Resolve a controller (class/function) from route and call it."""
        def handle_class(cls):
            meth = webapi.ctx.method
            if meth == 'HEAD' and not hasattr(cls, meth):
                meth = 'GET'
            if not hasattr(cls, meth):
                raise webapi.nomethod(cls)
            tocall = getattr(cls(), meth)
            return tocall(*args)

        def is_class(o):
            return isinstance(o, type)

        if f is None:
            raise webapi.notfound()
        elif isinstance(f, application):
            return f.handle_with_processors()
        elif is_class(f):
            return handle_class(f)
        elif isinstance(f, str):
            if f.startswith('redirect '):
                url = f.split(' ', 1)[1]
                if webapi.ctx.method == "GET":
                    q = webapi.ctx.env.get('QUERY_STRING', '')
                    if q:
                        url += '?' + q
                raise webapi.redirect(url)
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
            raise webapi.notfound()
