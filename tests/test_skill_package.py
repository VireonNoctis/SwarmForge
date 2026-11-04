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

    def test_capability_evidence_is_scoped_and_provenance_aware(self) -> None:
        contract = (ROOT / "docs" / "ADAPTER_CONTRACT.md").read_text(
            encoding="utf-8"
        )
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        for phrase in (
            "Evidence record and freshness",
            "session_context:",
            "client_version:",
            "observed_at:",
            "inventory_complete:",
            "evidence_kind:",
            "live_observation",
            "tool_inventory",
            "configuration",
            "official_documentation",
            "permission_scope:",
            "worker_session_id:",
            "terminal_state:",
            "evidence_ref:",
            "current-session inventory is complete",
            "never create a worker",
            "downgrade the capability to",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), contract.lower())

        for phrase in (
            "using the evidence record in `docs/ADAPTER_CONTRACT.md`",
            "Capability status is current-session evidence",
            "Do not invoke operations solely to probe",
            "If inventory or evidence is incomplete, use `unknown`",
        ):
            with self.subTest(skill_phrase=phrase):
                self.assertIn(phrase, skill)

    def test_adapter_contract_maps_native_host_lifecycle_without_assuming_parity(self) -> None:
        contract = (ROOT / "docs" / "ADAPTER_CONTRACT.md").read_text(
            encoding="utf-8"
        )
        sources = (ROOT / "docs" / "SOURCES.md").read_text(encoding="utf-8")

        contract_lower = contract.lower()
        self.assertIn("native-host lifecycle mapping", contract_lower)
        for phrase in (
            "claude code",
            "codex cli",
            "gemini cli",
            "worker.create",
            "worker.observe",
            "worker.collect_result",
            "worker.cancel",
            "workspace.isolate",
            "stable host-issued session identifier",
            "single-agent fallback",
            "not a portable lifecycle api",
            "do not automatically provide peer-team semantics",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), contract_lower)

        for url in (
            "https://code.claude.com/docs/en/sub-agents",
            "https://learn.chatgpt.com/docs/agent-configuration/subagents",
            "https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md",
            "https://github.com/google-gemini/gemini-cli/blob/main/docs/core/remote-agents.md",
        ):
            with self.subTest(url=url):
                self.assertIn(url, sources)

    def test_platform_compatibility_separates_host_and_api_capabilities(self) -> None:
        platform = (ROOT / "docs" / "PLATFORM_COMPATIBILITY.md").read_text(
            encoding="utf-8"
        )
        sources = (ROOT / "docs" / "SOURCES.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        platform_lower = platform.lower()
        for phrase in (
            "Skill packaging",
            "native subagents",
            "agent teams",
            "ordinary tool call",
            "provider API orchestration",
            "Gemini CLI",
            "ChatGPT Work",
            "Codex CLI",
            "Grok",
            "OpenAI Agents API",
            "Responses API",
            "experimental and disabled by default",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), platform_lower)

        for url in (
            "https://code.claude.com/docs/en/sub-agents",
            "https://code.claude.com/docs/en/agent-teams",
            "https://learn.chatgpt.com/docs/agent-configuration/subagents",
            "https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md",
            "https://docs.x.ai/developers/model-capabilities/text/multi-agent",
            "https://developers.openai.com/api/docs/guides/responses-multi-agent",
        ):
            with self.subTest(url=url):
                self.assertIn(url, sources)

        self.assertIn("ordinary tool calls", skill)
        self.assertIn("required worker lifecycle", skill)

    def test_skill_metadata_names_the_skill(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: swarmforge", text)
        self.assertIn("version: \"0.2.0\"", text)


if __name__ == "__main__":
    unittest.main()
