# coding: utf-8
from server.webapp import webapi

class application:
    def __init__(self, mapping=(), fvars=None):
        self.mapping = mapping
        self.fvars = fvars or {}

    def wsgifunc(self):
        def wsgi(env, start_resp):
            webapi.ctx = webapi.storage()
            webapi.ctx.env = env
            webapi.ctx.path = env.get('PATH_INFO', '/')
            webapi.ctx.fullpath = env.get('PATH_INFO', '/')
            webapi.ctx.method = env.get('REQUEST_METHOD', 'GET')

            try:
                result = self.handle_with_processors()
                if isinstance(result, list):
                    status, headers, body = result
                    start_resp(status, headers)
                    return body
                elif isinstance(result, (str, bytes)):
                    start_resp('200 OK', [('Content-Type', 'text/html')])
                    if isinstance(result, str):
                        return [result.encode('utf-8')]
                    else:
                        return [result]
                else:
                    start_resp('500 Internal Server Error', [('Content-Type', 'text/plain')])
                    return [b"Internal Server Error (Bad result type)"]

            except Exception as e:
                import traceback
                print(traceback.format_exc())
                start_resp('500 Internal Server Error', [('Content-Type', 'text/plain')])
                return [b"Internal Server Error"]

        return wsgi

    def handle_with_processors(self):
        return self._delegate(self.mapping, self.fvars, ())

    def _delegate(self, f, fvars, args=()):
        if isinstance(f, application):
            return f.handle_with_processors()
        if callable(f):
            return f()
        if isinstance(f, str):
            if f.startswith('redirect '):
                webapi.ctx.status = '301 Moved Permanently'
                webapi.ctx.headers = [('Location', f[9:])]
                return [
                    '301 Moved Permanently',
                    [('Location', f[9:])],
                    [b"Redirecting..."]
                ]
            elif '.' in f:
                mod, cls = f.rsplit('.', 1)
                mod = __import__(mod, None, None, [''])
                cls = getattr(mod, cls)
            else:
                cls = fvars[f]
            return self._delegate(cls, fvars, args)
        if isinstance(f, (tuple, list)):
            path = webapi.ctx.path
            print("[DEBUG] Matching path:", path)
            for pattern, what in f:
                if hasattr(pattern, 'match'):
                    match = pattern.match(path)
                    if match:
                        return self._delegate(what, fvars, match.groups())
                else:
                    if path == pattern:
                        return self._delegate(what, fvars, ())

        # Graceful 404 Not Found response
        print("DEBUG: No match found for path:", webapi.ctx.path)
        return [
            '404 Not Found',
            [('Content-Type', 'text/plain')],
            ["Not Found: {}".format(webapi.ctx.path).encode('utf-8')]
        ]
