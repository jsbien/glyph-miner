"""
This script runs the Glyph Miner server using Werkzeug's development WSGI server.

✅ Features:
- Auto-reloads on code changes (use_reloader=True)
- Interactive web-based debugger on exceptions (use_debugger=True)
- Runs on http://127.0.0.1:9099

🔍 Usage:
$ python3 utils/debug_wsgi_runner.py

💡 Tip:
When an exception occurs, you’ll see a traceback in the browser.
Click into any frame to inspect variables or run code interactively.

🚫 Do NOT use this in production — it’s for development only.
"""

import sys
import os

# Make sure project root is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server import server
from werkzeug.serving import run_simple

# Run the same WSGI app uwsgi uses, but with debugger support
run_simple("127.0.0.1", 9099, server.application, use_reloader=True, use_debugger=True)
