from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GeneratedRepositoryContractTests(unittest.TestCase):
    def test_metadata_is_valid(self):
        data = json.loads((ROOT / ".serve-template.json").read_text(encoding="utf-8"))
        self.assertIn(data["app_type"], {"gradio", "streamlit", "dash", "shiny", "custom"})
        self.assertGreaterEqual(int(data["app_port"]), 3000)
        self.assertLessEqual(int(data["app_port"]), 9999)
        self.assertIn(int(data["serve_uid"]), {999, 1000})
        self.assertTrue((ROOT / data["entrypoint"]).is_file())

    def test_strict_preflight(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/preflight.py"), "--root", str(ROOT), "--strict"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
