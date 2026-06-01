# Use cases

!!! warning "Draft — needs product owner input"
    This page is a skeleton. The scenarios below are accurate to what Trustabl
    does today, but the framing and priority are placeholders. Flesh out with
    real adoption stories and the positioning you want.

## CI gate on agent repos

Run Trustabl in CI and let its exit code fail the build when a reliability or
safety regression lands. Medium-and-above findings exit `1`; `--strict` fails on
any finding at all.

```sh
trustabl scan . --strict
```

Because the report is deterministic (identical inputs → identical `ScanID` and
byte-stable output), the same commit always produces the same result — no flaky
gate.

## Pull-request review via GitHub Code Scanning

Emit SARIF and upload it with `github/codeql-action/upload-sarif`. Findings then
appear as inline annotations on the pull request and in the repo's Security tab.

```sh
trustabl scan . --format sarif > trustabl.sarif
```

## Pre-merge / pre-release audit

Run a scan before cutting a release to catch agents wired without guardrails,
tools that shell out without an approval step, network calls without timeouts,
or a repo-wide permission bypass — the classes of problem ordinary linters miss.

## Hardening an existing agent codebase

Point Trustabl at an established repo to get a prioritized inventory of what
exists (every agent, tool, guardrail, MCP server, subagent) plus the weaknesses
attached to each. The per-tool and overall scores give a baseline to improve
against over time.

## Auditing a dependency or third-party agent

Scan a repo you don't own (locally or by URL) read-only to understand its agent
surface and risk posture before adopting it.

---

**Ideas to expand here:** concrete before/after stories, a sample CI workflow
file, screenshots of the human report and the SARIF annotations, and guidance on
which `--detectors` / `--strict` posture fits each scenario.
