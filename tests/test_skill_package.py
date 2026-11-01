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

    def test_worker_limit_gate_precedes_delegation(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        gate = text.index("## 0. Establish the worker limit before dispatch")
        discovery = text.index("## 1. Discover real delegation capabilities")
        self.assertLess(gate, discovery)
        self.assertIn("How many agents would you like to run for this task?", text)
        self.assertIn("wait for the answer", text)
        self.assertIn("maximum number of worker agents", text)

    def test_board_meeting_requires_real_participants_or_fallback(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## 2. Establish the engineering board", text)
        self.assertIn("Never fabricate attendees", text)
        self.assertIn("board unavailable — single-agent assessment", text)

    def test_task_graph_has_session_scoped_ids_and_explicit_lifecycle(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        patterns = (ROOT / "docs" / "ORCHESTRATION_PATTERNS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("task contract in `docs/ORCHESTRATION_PATTERNS.md`", skill)
        for field in (
            "session_id:",
            "owner:",
            "context_refs:",
            "read_paths:",
            "write_paths:",
            "depends_on:",
            "acceptance_criteria:",
            "verification_commands:",
            "deliverable:",
            "worker_session_id: null",
            "worker_status: null",
        ):
            with self.subTest(field=field):
                self.assertIn(field, patterns)
        self.assertIn("unique session ID", patterns)
        self.assertIn("reject cycles", patterns)
        self.assertIn("queued dispatch is not an active task", patterns)
        self.assertIn("completed", patterns)
        self.assertIn("failed", patterns)
        self.assertIn("cancelled", patterns)

    def test_worker_dispatch_requires_an_observable_lifecycle(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for capability in (
            "`worker.create`",
            "`worker.observe`",
            "`worker.collect_result`",
            "dispatch-ready",
            "single-agent fallback",
        ):
            with self.subTest(capability=capability):
                self.assertIn(capability, text)
        self.assertIn("Treat `unknown` as unavailable", text)
        self.assertIn("one worker at a time", text)

    def test_adapter_contract_defines_evidence_and_degradation(self) -> None:
        text = (ROOT / "docs" / "ADAPTER_CONTRACT.md").read_text(encoding="utf-8")
        for term in (
            "Normalized capability snapshot",
            "supported",
            "unsupported",
            "unknown",
            "worker.create",
            "worker.observe",
            "worker.collect_result",
            "Capacity exhausted",
            "Cancellation requested",
            "Result missing or mismatched task ID",
        ):
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_skill_metadata_names_the_skill(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: swarmforge", text)
        self.assertIn("version: \"0.2.0\"", text)


if __name__ == "__main__":
    unittest.main()
