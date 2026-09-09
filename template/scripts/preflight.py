#!/usr/bin/env python3
"""Validate a generated repository against the template's SciLifeLab Serve contract.

This script intentionally uses only the Python standard library so it can run before
application dependencies are installed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


PROFILES = {
    "gradio": {
        "port": 7860,
        "uid": 1000,
        "entrypoint": "app/main.py",
        "docker_markers": ["GRADIO_SERVER_NAME=0.0.0.0", "GRADIO_SERVER_PORT=7860", "GRADIO_TEMP_DIR="],
    },
    "streamlit": {
        "port": 8501,
        "uid": 1000,
        "entrypoint": "app/app.py",
        "docker_markers": ["--server.port=8501", "--server.address=0.0.0.0", "app.py"],
    },
    "dash": {
        "port": 8000,
        "uid": 1000,
        "entrypoint": "app/app.py",
        "docker_markers": ["gunicorn", "--bind=0.0.0.0:8000", "app:server"],
    },
    "shiny": {
        "port": 3838,
        "uid": 999,
        "entrypoint": "app/app.R",
        "docker_markers": ["/srv/shiny-server", "/usr/bin/shiny-server"],
    },
    "custom": {
        "port": 8000,
        "uid": 1000,
        "entrypoint": "app/app.py",
        "docker_markers": ["start-script.sh"],
    },
}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    oks: list[str] = field(default_factory=list)

    def ok(self, message: str) -> None:
        self.oks.append(message)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def require(self, condition: bool, success: str, failure: str) -> None:
        if condition:
            self.ok(success)
        else:
            self.error(failure)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def load_metadata(root: Path, report: Report) -> dict:
    path = root / ".serve-template.json"
    if not path.is_file():
        report.error("Missing .serve-template.json; regenerate/restore template metadata.")
        return {}
    try:
        data = json.loads(read_text(path))
    except (OSError, json.JSONDecodeError) as exc:
        report.error(f"Cannot read .serve-template.json: {exc}")
        return {}
    report.ok("Template metadata is readable")
    return data


def validate_required_files(root: Path, profile: dict, report: Report) -> None:
    required = [
        "Dockerfile",
        "README.md",
        "AGENTS.md",
        "DEPLOY.md",
        "SECURITY.md",
        "scripts/preflight.py",
        "scripts/docs_drift.py",
        "tests/test_contract.py",
        ".github/workflows/preflight.yml",
        ".github/workflows/docker-image-ghcr.yml",
        profile["entrypoint"],
        "app/AGENTS.md",
    ]
    for rel in required:
        report.require((root / rel).is_file(), f"Found {rel}", f"Missing required file: {rel}")


def validate_metadata(metadata: dict, app_type: str, profile: dict, report: Report) -> None:
    expected = {
        "app_type": app_type,
        "app_port": profile["port"],
        "serve_uid": profile["uid"],
        "entrypoint": profile["entrypoint"],
    }
    for key, value in expected.items():
        report.require(
            metadata.get(key) == value,
            f"Metadata {key}={value!r}",
            f"Metadata {key!r} should be {value!r}, got {metadata.get(key)!r}",
        )


def final_user(dockerfile: str) -> str | None:
    user = None
    for raw in dockerfile.splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and line.upper().startswith("USER "):
            user = line.split(None, 1)[1].strip()
    return user


def validate_dockerfile(root: Path, app_type: str, profile: dict, report: Report) -> None:
    path = root / "Dockerfile"
    if not path.is_file():
        return
    text = read_text(path)

    from_lines = [line.strip() for line in text.splitlines() if line.strip().upper().startswith("FROM ")]
    report.require(bool(from_lines), "Dockerfile has a FROM instruction", "Dockerfile has no FROM instruction")
    for line in from_lines:
        if re.search(r":latest(?:\s|$)", line, re.I):
            report.error("Dockerfile base image must not use the mutable :latest tag")

    report.require(
        re.search(rf"(?mi)^\s*EXPOSE\s+{profile['port']}\s*$", text) is not None,
        f"Dockerfile exposes port {profile['port']}",
        f"Dockerfile must EXPOSE {profile['port']}",
    )
    report.require("WORKDIR " in text, "Dockerfile defines WORKDIR", "Dockerfile must define WORKDIR")

    user = final_user(text)
    report.require(user is not None, "Dockerfile switches to a runtime USER", "Dockerfile must set a non-root runtime USER")
    if user is not None:
        report.require(user not in {"root", "0", "0:0"}, f"Final runtime USER is non-root ({user})", "Final Docker USER must not be root")

    uid = str(profile["uid"])
    report.require(uid in text, f"Dockerfile contains expected UID {uid}", f"Dockerfile should establish profile UID {uid}")

    for marker in profile["docker_markers"]:
        report.require(marker in text, f"Dockerfile contains {marker}", f"Dockerfile is missing required profile marker: {marker}")

    if app_type == "custom":
        start = root / "start-script.sh"
        report.require(start.is_file(), "Custom startup script exists", "Custom profile requires start-script.sh")
        if start.is_file():
            start_text = read_text(start)
            report.require("--host 0.0.0.0" in start_text, "Startup script binds to 0.0.0.0", "Custom startup script must bind to 0.0.0.0")
            report.require("--port 8000" in start_text, "Startup script uses port 8000", "Custom startup script must use port 8000")
        workdir_index = text.find("WORKDIR ")
        copy_index = text.find("COPY --chown=1000:1000 start-script.sh")
        report.require(copy_index > workdir_index >= 0, "Startup script is copied after WORKDIR is set", "Custom startup script must be placed in Docker WORKDIR")
        report.require("chmod +x ./start-script.sh" in text, "Startup script is made executable", "Custom startup script must be executable")

    if app_type == "gradio":
        report.require("GRADIO_ANALYTICS_ENABLED=False" in text, "Gradio analytics disabled", "Keep Gradio analytics disabled in the starter")

    if app_type == "shiny":
        report.require("USER shiny" in text, "Shiny runs as the shiny user", "Shiny profile must run as USER shiny")


def validate_python_requirements(root: Path, app_type: str, report: Report) -> None:
    if app_type == "shiny":
        return
    req = root / "app/requirements.txt"
    if not req.is_file():
        report.error("Python profile requires app/requirements.txt")
        return

    bad: list[str] = []
    dependencies = 0
    for raw in read_text(req).splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        dependencies += 1
        if line.startswith(("-e ", "git+", "http://", "https://")) or "==" not in line:
            bad.append(line)
    report.require(dependencies > 0, "Runtime requirements are present", "requirements.txt is empty")
    report.require(not bad, "Runtime requirements use exact == pins", "Unpinned/non-exact requirements: " + ", ".join(bad))


def app_text(root: Path) -> str:
    chunks: list[str] = []
    app = root / "app"
    if not app.exists():
        return ""
    for path in app.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".py", ".r", ".js", ".ts", ".txt", ".toml", ".yaml", ".yml"}:
            chunks.append(read_text(path))
    return "\n".join(chunks)


def validate_app_policy(root: Path, app_type: str, report: Report) -> None:
    text = app_text(root)

    if app_type == "gradio":
        report.require(re.search(r"share\s*=\s*False", text) is not None, "Gradio share=False is explicit", "Gradio starter must keep share=False")
        report.require(re.search(r"\bauth\s*=", text) is None, "No Gradio auth= found", "Do not add Gradio auth= on Serve")

    if app_type == "dash":
        report.require("server = app.server" in text, "Dash exposes server = app.server", "Dash app must expose server = app.server for Gunicorn")

    risky_auth = [
        r"streamlit[-_]authenticator",
        r"flask_login",
        r"django\.contrib\.auth",
        r"register_user\s*\(",
        r"create_user\s*\(",
    ]
    for pattern in risky_auth:
        if re.search(pattern, text, re.I):
            report.warn(f"Possible application account/authentication code detected ({pattern}); Serve does not allow user registration/user databases")


def validate_secret_hygiene(root: Path, report: Report) -> None:
    forbidden_names: list[Path] = []
    for base in [root, root / "app"]:
        if not base.exists():
            continue
        for path in base.iterdir():
            name = path.name.lower()
            if path.is_file() and (name == ".env" or name.startswith(".env.") or path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}):
                forbidden_names.append(path)
    report.require(not forbidden_names, "No obvious secret files found", "Do not commit secret files: " + ", ".join(str(p.relative_to(root)) for p in forbidden_names))

    patterns = {
        "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
        "GitHub token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    }
    findings: list[str] = []
    for path in (root / "app").rglob("*") if (root / "app").exists() else []:
        if not path.is_file() or path.stat().st_size > 1_000_000:
            continue
        content = read_text(path)
        for label, pattern in patterns.items():
            if pattern.search(content):
                findings.append(f"{label} in {path.relative_to(root)}")
    report.require(not findings, "No common credential patterns found in app/", "Possible committed credentials: " + ", ".join(findings))


def validate_workflows(root: Path, report: Report) -> None:
    preflight = root / ".github/workflows/preflight.yml"
    publish = root / ".github/workflows/docker-image-ghcr.yml"
    if not preflight.is_file() or not publish.is_file():
        return

    preflight_text = read_text(preflight)
    publish_text = read_text(publish)
    report.require("linux/amd64" in preflight_text, "CI build targets linux/amd64", "Preflight CI must build linux/amd64")
    report.require("linux/amd64" in publish_text, "Publish build targets linux/amd64", "Publish workflow must build linux/amd64")
    report.require("GITHUB_SHA" in publish_text and "date -u" in publish_text, "Publish workflow creates unique version tags", "Publish workflow should create timestamp/SHA image tags")
    latest_publish = re.search(r"(?:-t|--tag)\s+[^\s]+:latest\b|tags?:\s*[^\n]*:latest\b", publish_text, re.I)
    report.require(latest_publish is None, "Publish workflow does not publish :latest", "Publish workflow must not publish a :latest tag")
    report.require("packages: write" in publish_text, "Publish workflow has package write permission", "GHCR workflow needs packages: write")


def run(root: Path, strict: bool) -> int:
    report = Report()
    metadata = load_metadata(root, report)
    app_type = metadata.get("app_type") if metadata else None
    if app_type not in PROFILES:
        report.error(f"Unknown or missing app_type: {app_type!r}")
    else:
        profile = PROFILES[app_type]
        validate_metadata(metadata, app_type, profile, report)
        validate_required_files(root, profile, report)
        validate_dockerfile(root, app_type, profile, report)
        validate_python_requirements(root, app_type, report)
        validate_app_policy(root, app_type, report)
        validate_secret_hygiene(root, report)
        validate_workflows(root, report)

    for message in report.oks:
        print(f"[OK] {message}")
    for message in report.warnings:
        print(f"[WARN] {message}")
    for message in report.errors:
        print(f"[ERROR] {message}")

    print()
    print(f"Summary: {len(report.oks)} OK, {len(report.warnings)} warning(s), {len(report.errors)} error(s)")
    if report.errors or (strict and report.warnings):
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Generated project root (default: current directory)")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args()
    return run(args.root.resolve(), args.strict)


if __name__ == "__main__":
    sys.exit(main())
