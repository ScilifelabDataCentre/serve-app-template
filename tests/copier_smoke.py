#!/usr/bin/env python3
"""Run real Copier generation for every profile when Copier is installed."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ("gradio", "streamlit", "dash", "shiny", "custom")


def main() -> int:
    copier = shutil.which("copier")
    if not copier:
        print("[SKIP] Copier CLI is not installed in this environment.")
        return 0

    with tempfile.TemporaryDirectory(prefix="serve-template-copier-") as tmp:
        for app_type in PROFILES:
            dest = Path(tmp) / app_type
            cmd = [
                copier,
                "copy",
                "--defaults",
                "--data", f"app_type={app_type}",
                "--data", f"project_name=Smoke {app_type}",
                "--data", f"project_slug=smoke-{app_type}",
                "--data", "project_description=Copier smoke test",
                str(ROOT),
                str(dest),
            ]
            result = subprocess.run(cmd, text=True, capture_output=True)
            if result.returncode:
                print(result.stdout)
                print(result.stderr, file=sys.stderr)
                return result.returncode
            check = subprocess.run(
                [sys.executable, str(dest / "scripts/preflight.py"), "--root", str(dest), "--strict"],
                text=True,
                capture_output=True,
            )
            if check.returncode:
                print(check.stdout)
                print(check.stderr, file=sys.stderr)
                return check.returncode
            print(f"[OK] Copier generated {app_type}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
