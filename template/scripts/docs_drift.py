#!/usr/bin/env python3
"""Check live SciLifeLab Serve docs for markers relied on by this template.

This is intentionally a simple drift alarm. A failure means "read the current docs",
not "automatically change the template".
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

COMMON_URL = "https://serve.scilifelab.se/docs/application-hosting/other/"
FILES_URL = "https://serve.scilifelab.se/docs/files/"
PROFILE_URLS = {
    "gradio": "https://serve.scilifelab.se/docs/application-hosting/gradio/",
    "streamlit": "https://serve.scilifelab.se/docs/application-hosting/streamlit/",
    "dash": "https://serve.scilifelab.se/docs/application-hosting/dash/",
    "shiny": "https://serve.scilifelab.se/docs/application-hosting/shiny/",
    "custom": COMMON_URL,
}

COMMON_MARKERS = [
    "3000",
    "9999",
    "user id 1000",
    "start up script",
    "linux/amd64",
    "unique image tag",
    "sensitive data",
    "user database",
    "24 hours",
    "100 MB",
]
FILES_MARKERS = ["1 GB", "5 GB", "mount paths", "SQLite", "personal or sensitive data"]
PROFILE_MARKERS = {
    "gradio": ["7860", "GRADIO_SERVER_NAME", "1000", "known bug", "Public", "Link"],
    "streamlit": ["8501", "server.address=0.0.0.0", "1000", "app.py"],
    "dash": ["8000", "gunicorn", "app:server"],
    "shiny": ["3838", "999", "shiny-server", "/srv/shiny-server"],
    "custom": [],
}


def fetch(url: str, timeout: float) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "serve-template-docs-drift/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def check(name: str, text: str, markers: list[str]) -> list[str]:
    missing = [marker for marker in markers if marker.lower() not in text.lower()]
    if missing:
        print(f"[DRIFT] {name}: missing expected marker(s): {', '.join(missing)}")
    else:
        print(f"[OK] {name}: {len(markers)} expected marker(s) present")
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()

    metadata_path = args.root / ".serve-template.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        app_type = metadata["app_type"]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"[ERROR] Cannot load generated project metadata: {exc}")
        return 2

    if app_type not in PROFILE_URLS:
        print(f"[ERROR] Unknown app_type: {app_type}")
        return 2

    urls = {
        "common hosting guide": (COMMON_URL, COMMON_MARKERS),
        "file management": (FILES_URL, FILES_MARKERS),
    }
    if PROFILE_URLS[app_type] != COMMON_URL:
        urls[f"{app_type} guide"] = (PROFILE_URLS[app_type], PROFILE_MARKERS[app_type])

    failed = False
    for name, (url, markers) in urls.items():
        try:
            text = fetch(url, args.timeout)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"[ERROR] {name}: could not fetch {url}: {exc}")
            failed = True
            continue
        if check(name, text, markers):
            failed = True

    if failed:
        print("\nServe documentation may have changed, or the network fetch failed. Read the current pages before changing checks.")
        return 1
    print("\nNo expected documentation markers have drifted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
