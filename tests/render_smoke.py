#!/usr/bin/env python3
"""Render every profile with a small Copier-compatible Jinja harness and run checks.

This does not replace a real Copier invocation. It gives maintainers a dependency-light
way to catch broken Jinja, conditional paths, generated Python, YAML, and preflight rules.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from jinja2 import Environment, StrictUndefined

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "template"
PROFILES = {
    "gradio": dict(app_port=7860, serve_uid=1000, entrypoint="app/main.py", health_path="/", serve_doc_url="https://serve.scilifelab.se/docs/application-hosting/gradio/"),
    "streamlit": dict(app_port=8501, serve_uid=1000, entrypoint="app/app.py", health_path="/_stcore/health", serve_doc_url="https://serve.scilifelab.se/docs/application-hosting/streamlit/"),
    "dash": dict(app_port=8000, serve_uid=1000, entrypoint="app/app.py", health_path="/", serve_doc_url="https://serve.scilifelab.se/docs/application-hosting/dash/"),
    "shiny": dict(app_port=3838, serve_uid=999, entrypoint="app/app.R", health_path="/", serve_doc_url="https://serve.scilifelab.se/docs/application-hosting/shiny/"),
    "custom": dict(app_port=8000, serve_uid=1000, entrypoint="app/app.py", health_path="/health", serve_doc_url="https://serve.scilifelab.se/docs/application-hosting/other/"),
}


def env() -> Environment:
    e = Environment(undefined=StrictUndefined, keep_trailing_newline=True)
    e.filters["to_nice_yaml"] = lambda value: yaml.safe_dump(value, sort_keys=False)
    return e


def context(app_type: str) -> dict:
    values = {
        "project_name": f"Smoke {app_type.title()}",
        "project_slug": f"smoke-{app_type}",
        "project_description": "Template rendering smoke test.",
        "author_name": "Template Test",
        "app_type": app_type,
        "python_version": "3.12",
        "r_version": "4.4.1",
        "include_devcontainer": True,
        **PROFILES[app_type],
    }
    values["_copier_answers"] = {
        "_src_path": str(ROOT),
        "project_name": values["project_name"],
        "project_slug": values["project_slug"],
        "project_description": values["project_description"],
        "author_name": values["author_name"],
        "app_type": app_type,
        "python_version": values["python_version"],
        "r_version": values["r_version"],
        "include_devcontainer": True,
    }
    return values


def render_component(component: str, values: dict, is_file: bool) -> str:
    source = component[:-6] if is_file and component.endswith(".jinja") else component
    return env().from_string(source).render(**values)


def render_profile(app_type: str, destination: Path) -> None:
    values = context(app_type)
    destination.mkdir(parents=True, exist_ok=True)
    for source in sorted(TEMPLATE.rglob("*"), key=lambda p: (len(p.parts), str(p))):
        rel = source.relative_to(TEMPLATE)
        out_parts = []
        skip = False
        for index, part in enumerate(rel.parts):
            is_last = index == len(rel.parts) - 1
            rendered = render_component(part, values, is_file=(is_last and source.is_file()))
            if rendered == "":
                skip = True
                break
            out_parts.append(rendered)
        if skip:
            continue
        target = destination.joinpath(*out_parts)
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.name.endswith(".jinja"):
            text = env().from_string(source.read_text(encoding="utf-8")).render(**values)
            target.write_text(text, encoding="utf-8")
        else:
            shutil.copy2(source, target)


def assert_rendered(root: Path, app_type: str) -> None:
    meta = json.loads((root / ".serve-template.json").read_text(encoding="utf-8"))
    assert meta["app_type"] == app_type
    assert (root / "Dockerfile").is_file()
    assert (root / meta["entrypoint"]).is_file()
    assert (root / "app/AGENTS.md").is_file()
    assert len(list(root.glob("Dockerfile"))) == 1

    for path in root.rglob("*"):
        if not path.is_file() or path.stat().st_size > 1_000_000:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        assert "{%" not in text, f"unrendered Jinja block in {path}"
        assert re.search(r"(?<!\$)\{\{", text) is None, f"unrendered Jinja variable in {path}"

    for workflow in (root / ".github/workflows").glob("*.yml"):
        parsed = yaml.safe_load(workflow.read_text(encoding="utf-8"))
        assert isinstance(parsed, dict), f"invalid workflow YAML: {workflow}"

    for py in root.rglob("*.py"):
        result = subprocess.run([sys.executable, "-m", "py_compile", str(py)], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr

    result = subprocess.run(
        [sys.executable, str(root / "scripts/preflight.py"), "--root", str(root), "--strict"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(root / "tests"), "-v"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="serve-template-render-") as tmp:
        base = Path(tmp)
        for app_type in PROFILES:
            dest = base / app_type
            render_profile(app_type, dest)
            assert_rendered(dest, app_type)
            print(f"[OK] rendered and validated {app_type}")
    print("All five profiles passed render smoke tests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
