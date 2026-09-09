from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_copier_configuration_has_expected_profiles():
    config = yaml.safe_load((ROOT / "copier.yml").read_text(encoding="utf-8"))
    assert config["_subdirectory"] == "template"
    assert config["_templates_suffix"] == ".jinja"
    assert "app/**" in config["_skip_if_exists"]
    choices = config["app_type"]["choices"]
    assert set(choices.values()) == {"gradio", "streamlit", "dash", "shiny", "custom"}


def test_template_contains_shared_contract_files():
    required = [
        "README.md.jinja",
        "AGENTS.md.jinja",
        "DEPLOY.md.jinja",
        ".serve-template.json.jinja",
        "scripts/preflight.py",
        "scripts/docs_drift.py",
        "tests/test_contract.py",
        ".github/workflows/preflight.yml.jinja",
        ".github/workflows/docker-image-ghcr.yml.jinja",
        ".github/workflows/docs-drift.yml.jinja",
    ]
    for rel in required:
        assert (ROOT / "template" / rel).is_file(), rel


def test_every_profile_has_dockerfile_and_scoped_agent_file():
    source_paths = [str(p.relative_to(ROOT / "template")) for p in (ROOT / "template").rglob("*") if p.is_file()]
    for profile in ["gradio", "streamlit", "dash", "shiny", "custom"]:
        assert any(f"app_type == '{profile}'" in p and "Dockerfile" in p for p in source_paths), profile
        assert any(f"app_type == '{profile}'" in p and p.endswith("app{% endif %}/AGENTS.md.jinja") for p in source_paths), profile


def test_serve_requirement_audit_mentions_known_exceptions():
    text = (ROOT / "docs/SERVE_REQUIREMENTS.md").read_text(encoding="utf-8")
    assert "UID 999" in text
    assert "Private/Project" in text
    assert "template policy" in text.lower()
    assert "2026-09-08" in text

def test_agent_reference_dockerfiles_match_copier_templates_at_defaults():
    defaults = {"python_version": "3.12", "r_version": "4.4.1"}
    for profile in ["gradio", "streamlit", "dash", "shiny", "custom"]:
        matches = [
            path
            for path in (ROOT / "template").glob("*Dockerfile*.jinja")
            if f"app_type == '{profile}'" in path.name
        ]
        assert len(matches) == 1, profile
        expected = matches[0].read_text(encoding="utf-8")
        expected = expected.replace("{{ python_version }}", defaults["python_version"])
        expected = expected.replace("{{ r_version }}", defaults["r_version"])
        reference = ROOT / "profiles" / profile / "Dockerfile"
        assert reference.is_file(), profile
        assert reference.read_text(encoding="utf-8") == expected, profile

