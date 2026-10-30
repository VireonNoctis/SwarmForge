# Skill Development and Validation

SwarmForge is a portable Agent Skill. This document is for maintaining this repository; it is not a setup guide for a separate runtime.

## Install and use

Install the repository root as a Skill using the path documented by your AI host. The root must remain together with `SKILL.md` and the supporting files it references.

See:
- [Installation](INSTALLATION.md)
- [Platform compatibility](PLATFORM_COMPATIBILITY.md)

No compiled binary, package manager, API key, database, or external service is required to install or use the portable Skill. Live delegation depends on the capabilities the host exposes.

## Validate the package

Maintainers need Python 3 to run the standard-library validation tools:

~~~bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
~~~

Python is used only for package validation. It is not part of the Skill's runtime and is not required by users of the Skill.

The GitHub Actions workflow runs the same package checks on pushes and pull requests. Passing these checks validates package structure and smoke tests; it does not prove compatibility with every AI host or demonstrate 500 concurrent sessions.

## Optional external integrations

Do not create a backend as part of routine Skill installation or maintenance. If a separate external integration is explicitly approved, start with [Execution modes](EXECUTION_MODES.md) and [Adapter contract](ADAPTER_CONTRACT.md). Keep the integration optional and separate from the portable Skill.

## Preferred languages for a separately approved companion

The Skill itself has no language requirement. If future work explicitly calls for a separate implementation:

- **Rust** is the preferred language for the coordinator, scheduler, and worker lifecycle.
- **C++** is reserved for focused native integrations or performance-critical components with a demonstrated need.
- **Next.js** is reserved for an optional web interface that is separately requested.

Do not introduce these runtimes or a dashboard into this repository just to make the Skill installable. Any companion application should remain independently deployable and must not be required for the core Skill workflow.

## Before making capability claims

Check current official documentation for the specific host surface. Distinguish:
- Skill discovery from agent-spawning capability;
- a configured integration from one merely described in documentation;
- a queued task from an active worker session;
- design targets from measured runtime capacity.
