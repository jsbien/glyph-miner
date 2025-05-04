import sys
import types
import traceback
import server.webapp.webapi as webapi
from server.webapp.webapi import _NotFound, Redirect  # Let these propagate

class application:
    def __init__(self, mapping, fvars):
        self.mapping = mapping
        self.fvars = fvars or {}

        def resolve_route(self, path):
            """Match the path against self.mapping and return (handler_key, args)."""
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
# Add this line to match the route and update self.mapping properly:
            self.mapping, self.args = self._match(webapi.ctx.path)
            webapi.ctx.fullpath = env.get('PATH_INFO', '/')
            webapi.ctx.method = env.get('REQUEST_METHOD', 'GET')

            try:
                result = self.handle_with_processors()

                if not isinstance(result, (str, bytes, list, tuple)):
                    raise TypeError(f"Invalid response type: {type(result)}, value: {result}")

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

                # Fallback error
                start_resp('500 Internal Server Error', [('Content-Type', 'text/plain')])
                return [b"Internal Server Error"]

            except (_NotFound, Redirect):
                raise  # Let framework handle 404/redirects properly
            except Exception:
                print(traceback.format_exc())
                start_resp('500 Internal Server Error', [('Content-Type', 'text/plain')])
                return [b"Internal Server Error"]

        return wsgi

    # def handle_with_processors(self):
    #     return self._delegate(self.mapping, self.fvars, ())
    def handle_with_processors(self):
        try:
            print(f"[DEBUG] handle_with_processors(): self.mapping = {self.mapping}", flush=True)
            return self._delegate(self.mapping, self.fvars, ())

    def _delegate(self, f, fvars, args=[]):
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
                    x = webapi.ctx.env.get('QUERY_STRING', '')
                    if x:
                        url += '?' + x
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
