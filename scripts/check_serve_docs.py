#!/usr/bin/env python3
"""Template-maintainer drift check for all SciLifeLab Serve hosting profiles."""

from __future__ import annotations

import sys
import urllib.error
import urllib.request

PAGES = {
    "common": (
        "https://serve.scilifelab.se/docs/application-hosting/other/",
        [
            "3000", "9999", "user id 1000", "start up script", "linux/amd64",
            "unique image tag", "sensitive data", "user database", "24 hours", "100 MB",
            "2 vCPU", "4 GB", "12 vCPU", "48 GB", "mount paths",
        ],
    ),
    "files": (
        "https://serve.scilifelab.se/docs/files/",
        ["1 GB", "5 GB", "mount paths", "SQLite", "personal or sensitive data"],
    ),
    "fair": (
        "https://serve.scilifelab.se/docs/application-hosting/fair/",
        ["Specify a license", "Lock the versions", "CITATION.cff", "Zenodo", "README"],
    ),
    "gradio": (
        "https://serve.scilifelab.se/docs/application-hosting/gradio/",
        ["7860", "1000", "GRADIO_SERVER_NAME", "GRADIO_TEMP_DIR", "known bug", "Public", "Link"],
    ),
    "streamlit": (
        "https://serve.scilifelab.se/docs/application-hosting/streamlit/",
        ["8501", "1000", "server.address=0.0.0.0", "app.py"],
    ),
    "dash": (
        "https://serve.scilifelab.se/docs/application-hosting/dash/",
        ["8000", "gunicorn", "app:server", "linux/amd64"],
    ),
    "shiny": (
        "https://serve.scilifelab.se/docs/application-hosting/shiny/",
        ["3838", "999", "shiny-server", "/srv/shiny-server", "linux/amd64"],
    ),
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "serve-template-maintainer-drift/0.1"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def main() -> int:
    failed = False
    for name, (url, markers) in PAGES.items():
        try:
            text = fetch(url)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"[ERROR] {name}: fetch failed: {exc}")
            failed = True
            continue
        missing = [marker for marker in markers if marker.lower() not in text.lower()]
        if missing:
            print(f"[DRIFT] {name}: missing {', '.join(missing)}")
            failed = True
        else:
            print(f"[OK] {name}: {len(markers)} markers present")
    if failed:
        print("Read the current Serve docs and update docs/SERVE_REQUIREMENTS.md plus AGENTS files if the contract changed.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
