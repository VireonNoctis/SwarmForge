# SwarmForge Repository Instructions

These rules apply to the portable Skill and its supporting documentation.

## Before editing

1. Read the relevant sections of `SKILL.md` and supporting docs.
2. Inspect the current tree, tests, workflows, and existing conventions.
3. Verify Agent Skills format and provider behavior from current official documentation before adding compatibility claims.
4. Decide whether a change belongs in the portable Skill, platform-specific documentation, or an optional external integration contract.
5. Preserve the distinction between instructions and implemented runtime functionality.

## Engineering standards

- Prefer the smallest complete implementation.
- Keep vendor-specific behavior out of the portable Skill unless required.
- Keep native host delegation as the default execution path.
- Never make an external service, backend, database, or UI a requirement for Skill installation.
- Never invent tool names, CLI flags, endpoints, quotas, limits, or host support.
- Do not represent queued jobs or logical roles as running agents.
- Treat 500 as a design ceiling, not an unconditional guarantee.
- Keep optional companion implementations separate from this Skill package.
- Preserve existing repository hygiene, security checks, and dependency-light defaults.
- Never commit credentials, secrets, personal information, or production data.

## Language preferences for separate companion tools

The Skill itself is Markdown/YAML and does not need an application language. If a companion runtime is explicitly commissioned, prefer Rust for its core orchestration, C++ for narrow native/performance-critical components, and Next.js only for a separately requested web interface. Do not introduce these stacks without a concrete requirement.

## Verification

Run:

~~~bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
~~~

Also run project-specific formatters, linters, type checks, and builds when applicable. Validate Markdown links and YAML/JSON where relevant. Only report checks that were actually run. Do not claim a provider integration or 500-agent load test without a real implementation and evidence.

## Documentation

Update README.md when the product boundary or setup changes. Keep PLATFORM_COMPATIBILITY.md tied to current official sources. Update SOURCES.md when adding provider claims. Record major architecture decisions in `docs/DECISIONS/`.

## Git hygiene

- Keep commits focused and messages descriptive.
- Do not rewrite shared history or force-push unless explicitly requested.
- Do not create a Pull Request unless the implementation is massive throughout multiple files, equating to 5,000+ lines.
- Preserve the existing CI and security automation.
- Do not commit generated output, local IDE state, or environment-specific files.
