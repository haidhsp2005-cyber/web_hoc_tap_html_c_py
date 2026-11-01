import os
import sys

# Ensure the root project directory is on sys.path for Vercel Serverless
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.main import app as fastapi_app

# Vercel ASGI path-handling middleware
async def app(scope, receive, send):
    if scope.get("type") == "http":
        path = scope.get("path", "")

        # 1. Check if Vercel provided x-matched-path in headers
        headers = dict(scope.get("headers", []))
        matched = headers.get(b"x-matched-path")
        if matched:
            decoded_matched = matched.decode("utf-8")
            if not decoded_matched.startswith("/api/index"):
                # Use the original URL requested by client
                scope["path"] = decoded_matched

        # 2. Normalize path if rewritten to /api/index.py or /api
        current_path = scope.get("path", "")
        if current_path.startswith("/api/index.py"):
            new_p = current_path[len("/api/index.py"):]
            scope["path"] = new_p if new_p else "/"
        elif current_path.startswith("/api/index"):
            new_p = current_path[len("/api/index"):]
            scope["path"] = new_p if new_p else "/"
        elif current_path == "/api":
            scope["path"] = "/"
        elif current_path.startswith("/api/"):
            actual_apis = ("/api/submit", "/api/run-test", "/api/teacher")
            if not any(current_path.startswith(a) for a in actual_apis):
                scope["path"] = current_path[4:]

    await fastapi_app(scope, receive, send)
