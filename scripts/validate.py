#!/usr/bin/env python3
"""Validate SwarmForge's Skill package and retained repository configuration."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
CONFIG_FILES = (
    ".devcontainer/devcontainer.json",
    ".vscode/extensions.json",
    ".vscode/settings.json",
)
REQUIRED_DOCS = (
    "docs/ADAPTER_CONTRACT.md",
    "docs/ARCHITECTURE.md",
    "docs/EXECUTION_MODES.md",
    "docs/INSTALLATION.md",
    "docs/ORCHESTRATION_PATTERNS.md",
    "docs/PLATFORM_COMPATIBILITY.md",
    "docs/SCALING_TO_500.md",
    "docs/SECURITY_MODEL.md",
    "docs/SOURCES.md",
    "docs/WORKFLOWS.md",
)
ACTION_REFERENCE = re.compile(r"^[0-9a-fA-F]{40}$")
LINK = re.compile(r"!?\[[^]]*\]\(([^)]+)\)")
FIELD = re.compile(r"^([a-z][a-z0-9_-]*):\s*(.*?)\s*$")


def validate_json_files() -> list[str]:
    errors: list[str] = []
    for relative_path in CONFIG_FILES:
        path = ROOT / relative_path
        if not path.exists():
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{relative_path}: invalid JSON ({exc})")
    return errors


def validate_action_pins() -> list[str]:
    errors: list[str] = []
    workflow_root = ROOT / ".github" / "workflows"
    if not workflow_root.exists():
        return errors

    for path in sorted((*workflow_root.rglob("*.yml"), *workflow_root.rglob("*.yaml"))):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: cannot read workflow ({exc})")
            continue

        for line_number, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped.startswith("uses:"):
                continue
            reference = stripped.split(":", 1)[1].split("#", 1)[0].strip()
            reference = reference.strip(chr(39) + chr(34))
            if reference.startswith(("./", "docker://")):
                continue
            if "@" not in reference:
                errors.append(
                    f"{path.relative_to(ROOT)}:{line_number}: "
                    f"Action reference is not pinned: {reference}"
                )
                continue
            revision = reference.rsplit("@", 1)[1]
            if not ACTION_REFERENCE.fullmatch(revision):
                errors.append(
                    f"{path.relative_to(ROOT)}:{line_number}: "
                    f"Action must use a full 40-character commit SHA: {reference}"
                )
    return errors


def validate_skill_frontmatter() -> list[str]:
    errors: list[str] = []
    try:
        text = SKILL.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"SKILL.md: cannot read ({exc})"]

    if not text.startswith("---\n"):
        return ["SKILL.md: frontmatter must begin on line 1"]
    end = text.find("\n---\n", 4)
    if end < 0:
        return ["SKILL.md: frontmatter closing delimiter is missing"]

    values: dict[str, str] = {}
    for number, line in enumerate(text[4:end].splitlines(), 2):
        if not line or line.startswith((" ", "\t", "#")):
            continue
        match = FIELD.fullmatch(line)
        if match:
            values[match.group(1)] = match.group(2).strip().strip(chr(39) + chr(34))
        else:
            errors.append(f"SKILL.md:{number}: unsupported frontmatter line")

    name = values.get("name", "")
    description = values.get("description", "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        errors.append("SKILL.md: name must be a lowercase hyphenated slug (max 64 chars)")
    if not description or len(description) > 1024:
        errors.append("SKILL.md: description is required and must be <= 1024 chars")
    if len(values.get("compatibility", "")) > 500:
        errors.append("SKILL.md: compatibility must be <= 500 chars")
    return errors


def validate_local_links() -> list[str]:
    errors: list[str] = []
    candidates = [ROOT / "README.md", SKILL]
    candidates.extend((ROOT / "docs").rglob("*.md"))

    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{path.relative_to(ROOT)}: cannot read ({exc})")
            continue

        for raw in LINK.findall(text):
            target = raw.strip().split("#", 1)[0].strip()
            if not target or urlparse(target).scheme or target.startswith("/"):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(
                    f"{path.relative_to(ROOT)}: local link escapes repository: {target}"
                )
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)}: broken local link: {target}")
    return errors


def main() -> int:
    errors = validate_json_files()
    errors.extend(validate_action_pins())
    errors.extend(validate_skill_frontmatter())

    for relative_path in REQUIRED_DOCS:
        if not (ROOT / relative_path).is_file():
            errors.append(f"required documentation missing: {relative_path}")

    if not (ROOT / "tests" / "test_skill_package.py").is_file():
        errors.append("required smoke tests missing: tests/test_skill_package.py")

    errors.extend(validate_local_links())

    if errors:
        print("\n".join(f"ERROR: {item}" for item in errors), file=sys.stderr)
        return 1
    print("SwarmForge Skill package checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
