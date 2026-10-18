import os
import sys

# Ensure the root directory is on the Python module search path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import Flask WSGI application instance
from app import app

# Vercel Serverless Function entry point
# Vercel automatically exposes the 'app' variable as the WSGI callable
