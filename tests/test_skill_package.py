"""Smoke tests for the SwarmForge Skill package."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SkillPackageTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertIn("checks passed", result.stdout)

    def test_root_skill_entrypoint_exists(self) -> None:
        path = ROOT / "SKILL.md"
        self.assertTrue(path.is_file())
        self.assertTrue(path.read_text(encoding="utf-8").startswith("---\n"))

    def test_skill_metadata_names_the_skill(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: swarmforge", text)
        self.assertIn("version: \"0.2.0\"", text)


if __name__ == "__main__":
    unittest.main()
