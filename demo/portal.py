#!/usr/bin/env python3
"""A fictional time & billing portal. Stands in for the real, closed system.

Run:  python3 demo_portal.py   (serves on http://localhost:8484)

Log in through a browser at /login (any username, password "letmein") and the
portal sets a session cookie. The JSON endpoints under /api/ answer only to
that cookie — exactly the shape of a portal that "has no API": the API is
there, it just answers to nothing but a browser session.
"""
import http.cookies
import http.server
import json
import secrets
import urllib.parse

SESSIONS = set()

TIMESHEET = [
    {"week": "2026-08-10", "client": "Acme Corp", "hours": 34.0, "billed": True},
    {"week": "2026-08-17", "client": "Acme Corp", "hours": 38.5, "billed": False},
    {"week": "2026-08-17", "client": "Initech", "hours": 4.0, "billed": False},
]
INVOICES = [
    {"id": "INV-2201", "client": "Acme Corp", "amount": 18400.00, "status": "paid"},
    {"id": "INV-2202", "client": "Acme Corp", "amount": 21075.00, "status": "open"},
    {"id": "INV-2203", "client": "Initech", "amount": 2200.00, "status": "disputed"},
]

LOGIN_PAGE = """<!doctype html><title>TimePortal</title>
<h1>TimePortal</h1><form method=post action=/login>
<input name=user placeholder=username> <input name=pw type=password placeholder=password>
<button>Log in</button></form><p>(any username, password "letmein")</p>"""


class Portal(http.server.BaseHTTPRequestHandler):
    def _session_ok(self):
        c = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
        return "portal_session" in c and c["portal_session"].value in SESSIONS

    def _json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/login":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(LOGIN_PAGE.encode())
        elif self.path.startswith("/api/"):
            if not self._session_ok():
                self._json({"error": "no session"}, 401)
            elif self.path == "/api/timesheet":
                self._json(TIMESHEET)
            elif self.path == "/api/invoices":
                self._json(INVOICES)
            else:
                self._json({"error": "not found"}, 404)
        else:
            self.send_response(302)
            self.send_header("Location", "/login")
            self.end_headers()

    def do_POST(self):
        if self.path == "/login":
            length = int(self.headers.get("Content-Length", 0))
            form = urllib.parse.parse_qs(self.rfile.read(length).decode())
            if form.get("pw", [""])[0] == "letmein":
                token = secrets.token_hex(16)
                SESSIONS.add(token)
                self.send_response(302)
                self.send_header("Set-Cookie", f"portal_session={token}; HttpOnly")
                self.send_header("Location", "/login")
                self.end_headers()
                return
            self.send_response(403)
            self.end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print("TimePortal on http://localhost:8484  (password: letmein)")
    http.server.HTTPServer(("127.0.0.1", 8484), Portal).serve_forever()
