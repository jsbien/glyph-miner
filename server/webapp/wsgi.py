"""
WSGI Utilities
(from webapp.py)
"""

import os
import sys

from . import webapi as webapp
from .utils import listget
from .net import validaddr, validip
import httpserver

def runfcgi(func, addr=('localhost', 8000)):
    """Runs a WSGI function as a FastCGI server."""
    import flup.server.fcgi as flups
    return flups.WSGIServer(func, multiplexed=True, bindAddress=addr, debug=False).run()

def runscgi(func, addr=('localhost', 4000)):
    """Runs a WSGI function as an SCGI server."""
    import flup.server.scgi as flups
    return flups.WSGIServer(func, bindAddress=addr, debug=False).run()

def runwsgi(func):
    """
    Runs a WSGI-compatible `func` using FCGI, SCGI, or a simple webapp server,
    as appropriate based on context and `sys.argv`.
    """
    from .web_http import runsimple  # <-- Lazy import to avoid circular dependency

    if os.environ.get('SERVER_SOFTWARE'): # cgi
        os.environ['FCGI_FORCE_CGI'] = 'Y'

    if (os.environ.get('PHP_FCGI_CHILDREN')  # lighttpd fastcgi
        or os.environ.get('SERVER_SOFTWARE')):
        return runfcgi(func, None)

    if 'fcgi' in sys.argv or 'fastcgi' in sys.argv:
        args = sys.argv[1:]
        if 'fastcgi' in args: args.remove('fastcgi')
        elif 'fcgi' in args: args.remove('fcgi')
        if args:
            return runfcgi(func, validaddr(args[0]))
        else:
            return runfcgi(func, None)

    if 'scgi' in sys.argv:
        args = sys.argv[1:]
        args.remove('scgi')
        if args:
            return runscgi(func, validaddr(args[0]))
        else:
            return runscgi(func)

    return runsimple(func, validip(listget(sys.argv, 1, '')))

def _is_dev_mode():
    argv = getattr(sys, "argv", [])

    if os.environ.get('SERVER_SOFTWARE') \
        or os.environ.get('PHP_FCGI_CHILDREN') \
        or 'fcgi' in argv or 'fastcgi' in argv \
        or 'mod_wsgi' in argv:
            return False
    return True

# When running the builtin-server, enable debug mode if not already set.
webapp.config.setdefault('debug', _is_dev_mode())
