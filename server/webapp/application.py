# coding: utf-8
from server.webapp import webapi
# for debugging
import datetime
from server.webapp.webapi import _NotFound, Redirect


class application:
    def __init__(self, mapping=(), fvars=None):
        self.mapping = mapping
        self.fvars = fvars or {}

    def wsgifunc(self):
        def wsgi(env, start_resp):
            webapi.ctx = webapi.storage()
            webapi.ctx.headers = []
            webapi.ctx.env = env
            webapi.ctx.path = env.get('PATH_INFO', '/')
            webapi.ctx.fullpath = env.get('PATH_INFO', '/')
            webapi.ctx.method = env.get('REQUEST_METHOD', 'GET')

            try:
                result = self.handle_with_processors()
                print(f"[DEBUG] handler returned: {result!r}")
                if not isinstance(result, (str, bytes, list, tuple)):
                    raise TypeError(f"Invalid response type: {type(result)}, value: {result}")

                if isinstance(result, list):
                    import datetime
                    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                    with open(f"./debug-wsgi-return-{ts}.log", "w") as debug_file:
                        debug_file.write(f"result from handler: {repr(result)}\n")
                        debug_file.write(f"type: {type(result)}\n")
                        debug_file.write(f"list length: {len(result)}\n")
                        debug_file.write(f"first: {type(result[0])}, second: {type(result[1])}, third: {type(result[2])}\n")

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

            except (_NotFound, Redirect):
                raise
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                start_resp('500 Internal Server Error', [('Content-Type', 'text/plain')])
                return [b"Internal Server Error"]

            # except _NotFound as e:
            #     return e()
            # except Redirect as e:
            #     return e()
                
            # except webapi.notfound as e:
            #     return e()
            # except webapi.redirect as e:
            #     return e()
            # except Exception as e:
            #     import traceback
            #     print(traceback.format_exc())
            #     start_resp('500 Internal Server Error', [('Content-Type', 'text/plain')])
            #     return [b"Internal Server Error"]


             # except Exception as e:
             #     import traceback
             #     print(traceback.format_exc())
             #     start_resp('500 Internal Server Error', [('Content-Type', 'text/plain')])
             #    return [b"Internal Server Error"]



        return wsgi
    def handle_with_processors(self):
        return self._delegate(self.mapping, self.fvars, ())
#        return self._delegate(self.mapping, handler_map, ())


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
                print(f">>> Looking up handler: {f} in fvars: {list(fvars.keys())}", flush=True)
                cls = fvars[f]
            return handle_class(cls)
        elif hasattr(f, '__call__'):
            return f()
        else:
            raise webapi.notfound()
#            return webapi.notfound()
    
#     def _delegate(self, f, fvars, args=()):
# #        import datetime
#         timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

#         try:
#             with open(f"./debug-request-path-{timestamp}.log", "w") as debugf:
#                 debugf.write(f"Starting path debugging\n") 
#                 path = getattr(webapi.ctx, "path", "(no ctx.path)")
#                 debugf.write(f"web.ctx.path = {path}\n") 
# #                debugf.write(f"web.ctx.path = {web.ctx.path}\n")
#         except Exception as e:
#             pass

#         if isinstance(f, application):
#             return f.handle_with_processors()
#         if callable(f):
#             return f()
#         if isinstance(f, str):
#             if f.startswith('redirect '):
#                 webapi.ctx.status = '301 Moved Permanently'
#                 webapi.ctx.headers = [('Location', f[9:])]
#                 return [
#                     '301 Moved Permanently',
#                     [('Location', f[9:])],
#                     [b"Redirecting..."]
#                 ]
#             elif '.' in f:
#                 mod, cls = f.rsplit('.', 1)
#                 mod = __import__(mod, None, None, [''])
#                 cls = getattr(mod, cls)
#             else:
#                 try:
#                     timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
#                     with open(f"./debug-delegate-resolve-{timestamp}.log", "w") as df:
#                         df.write(f"Trying to resolve handler: {repr(f)}\n")
#                         df.write(f"Handler in fvars: {f in fvars}\n")
#                         df.write(f"Available keys in fvars: {list(fvars.keys())}\n")
#                 except Exception:
#                     pass

#                 cls = fvars[f]
#                 try:
#                     ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
#                     with open(f"./debug-delegate-invoke-{ts}.log", "w") as debug_file:
#                         debug_file.write(f"Resolved {repr(f)} to: {cls}\n")
#                         debug_file.write(f"Type: {type(cls)}\n")
#                         try:
#                             instance = cls()
#                             debug_file.write("Handler instantiated successfully\n")
#                             debug_file.write(f"Has GET: {hasattr(instance, 'GET')}\n")
#                             if hasattr(instance, 'GET'):
#                                 result = instance.GET()
#                                 debug_file.write(f"GET() returned: {repr(result)}\n")
#                                 return result
#                         except Exception as e:
#                             debug_file.write(f"Exception when calling handler: {e}\n")
#                 except Exception:
#                     pass

#                 instance = cls()

#                 if hasattr(instance, 'GET'):
#                     result = instance.GET()
#                     return result
#                 else:
#                     return self._delegate(cls, fvars, args)

#             return self._delegate(cls, fvars, args)
#         if isinstance(f, (tuple, list)):
#             path = webapi.ctx.path
#             print("[DEBUG] Matching path:", path)

#             # DEBUG dump to timestamped file
#             try:
#                 timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
#                 filename = f"./debug-delegate-urls-{timestamp}.log"
#                 with open(filename, "w") as f_debug:
#                     f_debug.write(f"Type of f: {type(f)}\n")
#                     for i, item in enumerate(f):
#                         f_debug.write(f"f[{i}] = {repr(item)} (type: {type(item)})\n")
#             except Exception as e:
#                 # Avoid crashing if debug write fails
#                 pass


#             for i in range(0, len(f), 2):
#                 pattern = f[i]
#                 what = f[i + 1]
# #            for pattern, what in f:
#                 if hasattr(pattern, 'match'):
#                     match = pattern.match(path)
#                     if match:
#                         try:
#                             timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
#                             with open(f"./debug-resolve-delegate-{timestamp}.log", "w") as df_out:
#                                 df_out.write(f"Delegating to: {repr(what)}\n")
#                                 df_out.write(f"Is str: {isinstance(what, str)}\n")
#                                 df_out.write(f"Keys in fvars: {list(fvars.keys())}\n")
#                                 df_out.write(f"{repr(what)} in fvars: {what in fvars}\n")
#                         except Exception:
#                             pass

#                         return self._delegate(what, fvars, match.groups())
#                 else:
#                     if path == pattern:
#                         return self._delegate(what, fvars, ())

#         # Graceful 404 Not Found response
#         print("DEBUG: No match found for path:", webapi.ctx.path)
#         return [
#             '404 Not Found',
#             [('Content-Type', 'text/plain')],
#             ["Not Found: {}".format(webapi.ctx.path).encode('utf-8')]
#         ]
