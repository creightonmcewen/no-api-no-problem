#!/usr/bin/env python3
"""portal_client — talk to a portal that has no API.

Rung 1 of the ladder: the browser holds the session, this tool borrows it.
Nothing here logs in, stores a password, or scrapes a page. It reads the
cookie the browser already has and calls the JSON the page itself calls.

    python3 portal_client.py hours --unbilled
    python3 portal_client.py invoices --status open --json

Against the bundled demo portal:

    python3 demo_portal.py                 # terminal 1
    # log in at http://localhost:8484/login (password: letmein)
    python3 portal_client.py hours         # terminal 2

Cookie source, in order of preference:
  1. --cookie / PORTAL_SESSION  — an explicit session value (rung 2: harvested once)
  2. pycookiecheat              — read Chrome's own cookie store (rung 1: nothing to harvest)

Real portals differ only in the endpoint names. Find them once with DevTools →
Network → XHR while you use the page normally. What the page fetches, you can fetch.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("PORTAL_BASE", "http://localhost:8484")


def session_cookie(explicit=None):
    """Return the portal session value, or exit with a usable message."""
    if explicit:
        return explicit
    if os.environ.get("PORTAL_SESSION"):
        return os.environ["PORTAL_SESSION"]
    try:
        from pycookiecheat import chrome_cookies
    except ImportError:
        sys.exit(
            "No session. Either pass --cookie / set PORTAL_SESSION, "
            "or install pycookiecheat to read the browser's own store:\n"
            "    pip install pycookiecheat"
        )
    jar = chrome_cookies(BASE)
    if "portal_session" not in jar:
        sys.exit(f"No portal session in the browser's cookie store. Log in at {BASE}/login first.")
    return jar["portal_session"]


def get(path, cookie):
    req = urllib.request.Request(f"{BASE}{path}")
    req.add_header("Cookie", f"portal_session={cookie}")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            sys.exit("Session rejected — it expired, or the browser logged out. Log in again.")
        sys.exit(f"Portal returned {e.code} for {path}")
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach {BASE} ({e.reason})")


def emit(rows, as_json, columns):
    """Print for a human by default, for an agent with --json."""
    if as_json:
        print(json.dumps(rows, indent=2))
        return
    if not rows:
        print("(nothing)")
        return
    widths = [max(len(str(r[c])) for r in rows + [{c: c for c in columns}]) for c in columns]
    print("  ".join(c.upper().ljust(w) for c, w in zip(columns, widths)))
    for r in rows:
        print("  ".join(str(r[c]).ljust(w) for c, w in zip(columns, widths)))


def main():
    # Shared flags live on a parent so they work on either side of the
    # subcommand — `--json invoices` and `invoices --json` both parse.
    # SUPPRESS matters: without it the subparser's own default overwrites a
    # value given before the subcommand, and --cookie silently goes missing.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--cookie",
        default=argparse.SUPPRESS,
        help="session value (otherwise read from the browser)",
    )
    common.add_argument(
        "--json",
        action="store_true",
        default=argparse.SUPPRESS,
        help="machine-readable output",
    )

    p = argparse.ArgumentParser(
        description="Query a portal that publishes no API.", parents=[common]
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    hours = sub.add_parser("hours", help="timesheet weeks", parents=[common])
    hours.add_argument("--unbilled", action="store_true", help="only unbilled weeks")

    inv = sub.add_parser("invoices", help="invoices", parents=[common])
    inv.add_argument("--status", help="filter by status (paid, open, disputed)")

    args = p.parse_args()
    cookie = session_cookie(getattr(args, "cookie", None))
    as_json = getattr(args, "json", False)

    if args.cmd == "hours":
        rows = get("/api/timesheet", cookie)
        if args.unbilled:
            rows = [r for r in rows if not r["billed"]]
        emit(rows, as_json, ["week", "client", "hours", "billed"])
    else:
        rows = get("/api/invoices", cookie)
        if args.status:
            rows = [r for r in rows if r["status"] == args.status]
        emit(rows, as_json, ["id", "client", "amount", "status"])


if __name__ == "__main__":
    main()
