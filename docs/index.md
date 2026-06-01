# Trustabl

**Trustabl is a static analyzer for agent reliability.** It scans a repository
that builds AI agents — using the Claude Agent SDK, the OpenAI Agents SDK, or
Google ADK — discovers every agent, tool, guardrail, and configuration in the
code, and reports the reliability and safety weaknesses it finds.

It runs as a single binary, reads your repo without writing anything into it,
and produces a deterministic report you can read by eye, pipe as JSON, or upload
to GitHub Code Scanning as SARIF.

## The problem it addresses

Agent code fails in ways ordinary linters don't see. A tool that shells out
without a human-approval step, an agent wired with no input guardrails, a
network call with no timeout, a project that sets `bypassPermissions`
repo-wide — none of these are syntax errors, but each is a real reliability or
safety hazard. Trustabl knows the shapes of the major agent SDKs and checks for
exactly these problems.

## How it works, in one breath

A flat, deterministic pipeline: **recon** (cheap, no parsing) →
**inventory** (per-language AST discovery of tools/agents/guardrails) →
**policy selection** (load only the rule packs for the SDKs actually present) →
**analysis** (run scope-aware detectors against typed inputs) → **scoring**.
Identical inputs always produce an identical report. See
[How it works → Architecture](how-it-works/architecture.md) for the full detail.

## What it covers

- **Claude Agent SDK** — Python and TypeScript
- **OpenAI Agents SDK** — Python and TypeScript
- **Google ADK** — Python and TypeScript
- **MCP** tool registrations and config files
- **Shell-invocation** risk surface (`subprocess` / `os.system` / `os.popen`)

The full SDK-by-language matrix is on the [Coverage](coverage.md) page.

## Where to go next

- **[Installation](installation.md)** — Homebrew, Scoop, Docker, or a direct binary
- **[Quick start](quick-start.md)** — your first scan in two commands
- **[Use cases](use-cases.md)** — CI gates, pre-merge audits, agent hardening
- **[CLI reference](cli-reference.md)** — every flag and exit code
- **[Rules](rules/index.md)** — every check Trustabl runs, with the threat model behind it

!!! note "Two-part project"
    The **engine** (this scanner) and its **detection rules** live in separate
    repositories. The engine ships with no rules embedded; it resolves them at
    scan time from the
    [`trustabl-rules`](https://github.com/trustabl/trustabl-rules) repository.
    That is why a rule can be added or updated without rebuilding the binary.
