import sys
import os

# Make sure project root is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server import server
from werkzeug.serving import run_simple

# Run the same WSGI app uwsgi uses, but with debugger support
run_simple("127.0.0.1", 9099, server.application, use_reloader=True, use_debugger=True)
