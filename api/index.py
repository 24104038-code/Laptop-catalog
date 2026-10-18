import os
import sys

# Ensure the root directory is on the Python module search path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app


class VercelPathFixer:
    """
    WSGI Middleware that normalizes request paths on Vercel.
    When Vercel rewrites incoming traffic to /api/index, PATH_INFO can
    contain '/api/index' or '/api' prefixes. This middleware strips those
    prefixes so Flask's standard routes ('/', '/add-product', '/product/<id>', etc.)
    always match cleanly with zero 404 errors.
    """

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # 1. Check if Vercel provided the original client request path in headers
        raw_path = environ.get("HTTP_X_FORWARDED_URI") or environ.get("HTTP_X_MATCHED_PATH")
        if raw_path and not raw_path.startswith("/api/"):
            path = raw_path.split("?")[0]
            environ["PATH_INFO"] = path
        else:
            # 2. Otherwise strip any internal Vercel /api/index or /api prefix
            path = environ.get("PATH_INFO", "")
            for prefix in ["/api/index.py", "/api/index", "/api"]:
                if path.startswith(prefix):
                    path = path[len(prefix):]
                    break
            if not path or path == "":
                path = "/"
            environ["PATH_INFO"] = path

        return self.wsgi_app(environ, start_response)


# Wrap Flask application with VercelPathFixer middleware
app.wsgi_app = VercelPathFixer(app.wsgi_app)
