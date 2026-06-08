# Use cases

Trustabl is a **read-only** static analyzer: it inspects agent code without
running it and without writing anything into the repo (remote targets are
shallow-cloned to a temp dir and removed on exit). Every scenario below is built
on the shipped feature set — discovery across nine agent SDKs, the five-scope
rule engine (tool, agent, subagent, skill, repo), the deterministic report, the
JSON / SARIF outputs, and the opt-in dependency vulnerability scan.

## Gate agent code in CI

Run Trustabl in your pipeline and let its exit code fail the build on a
reliability or safety regression. The exit code is a contract:

- `0` — no findings at or above **medium** severity
- `1` — a finding ≥ medium is present (or **any** finding under `--strict`)
- `2` — scanner error, or no usable rules were available

```sh
# Fail the build on any finding, regardless of severity
trustabl scan . --strict
```

Because the report is **deterministic** — identical inputs always produce an
identical `ScanID` and byte-stable output — the same commit always yields the
same result. The gate never flakes, and a `2` (rather than a misleading clean
pass) tells you when rules could not be resolved at all.

## Annotate pull requests with GitHub Code Scanning

Emit SARIF 2.1.0 and upload it with `github/codeql-action/upload-sarif`.
Findings then surface as inline annotations on the pull request and in the
repository's **Security → Code scanning** tab.

```yaml
# .github/workflows/trustabl.yml
- run: trustabl scan . --format sarif > trustabl.sarif
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trustabl.sarif
```

Findings carry stable fingerprints, so Code Scanning deduplicates the same issue
across runs instead of re-opening it on every push.

## Self-audit while the agent writes code

Shift left of CI entirely: run Trustabl as a local stdio MCP server so an MCP
client (Claude Code, Cursor, Claude Desktop) can scan code an agent just wrote
and read the findings back before anything is committed.

```sh
# Register the bundled scan tool with Claude Code
claude mcp add trustabl -- trustabl mcp
```

It exposes the same scan as `trustabl scan` — same findings, same JSON shape —
as an MCP `scan` tool, and opens no network port. The Claude Code plugin under
`.claude-plugin/` wires this into a scan-and-fix loop that triggers right after
agent, tool, subagent, or MCP-server code is written.

## Catch vulnerable dependencies and export an SBOM

Beyond the agent-specific rules, Trustabl can audit the repo's supply chain. The
dependency scan is deterministic and offline by default; the CVE match is
explicitly opt-in and online.

```sh
# Export a CycloneDX SBOM of declared deps (pure inventory, no network)
trustabl scan . --bom-out sbom.json

# Match pinned deps against the OSV database and FAIL on known CVEs
trustabl scan . --vuln-scan

# One pass: CycloneDX BOM + VEX (vulnerabilities[]) in a single artifact
trustabl scan . --vuln-scan --bom-out bom.json
```

`--bom-out` writes a CycloneDX 1.5 BOM of the declared direct dependencies
across every supported language (pip / npm / Go / Composer / NuGet / Cargo).
`--vuln-scan` matches the repo's concretely-pinned dependencies against a pinned
OSV snapshot and reports each affected package as a finding carrying the advisory
ID (CVE / GHSA / PYSEC), a CVSS-derived severity, and the first fixed version —
so a vulnerable dependency fails the scan through the normal severity gate and
exit codes. The OSV snapshot is fetched once and cached (`trustabl vulndb pull`
pre-warms it), so repeated scans are fast and offline-capable.

## Run a pre-release safety audit

Scan before cutting a release to catch the classes of problem ordinary linters
don't model — drawn directly from the shipped rule packs:

- a tool that **shells out or executes code** with no human-approval step
- a **network call without a timeout** that can hang an agent run
- an **agent wired without input/output guardrails**
- an **unnormalized filesystem path** flowing into an I/O call
- a project-wide **permission-mode bypass** (`bypassPermissions` in
  `.claude/settings.json` or `ClaudeAgentOptions`)

```sh
trustabl scan . --format json > audit.json
```

Each finding explains *why* it matters and suggests a fix, and a per-tool plus
overall reliability score summarizes the repo.

## Inventory and baseline an existing agent codebase

Point Trustabl at an established repo to get a structured inventory of
everything it builds — agents, tools, guardrails, subagents, MCP servers,
hosted tools — with each weakness attributed to the **specific agent or tool**,
not flattened to the repo. The overall score gives a baseline to improve
against over time.

Trustabl is also honest about its blind spots: if your repo uses an SDK it
doesn't yet audit, it emits an explicit *"unaudited SDK"* finding rather than
reporting a falsely clean result.

## Audit a third-party or dependency agent repo

Assess a repo you don't own before adopting it. Scanning is read-only and works
straight from a URL — nothing is written to the target, locally or remotely.

```sh
trustabl scan https://github.com/org/their-agent-repo
```

## Scan in air-gapped or offline environments

Rules are resolved once and cached under your OS cache directory. In a locked-down
or offline environment, pre-fetch the rule packs where you have connectivity and
then scan against the cache only:

```sh
trustabl rules pull            # where you have network access
trustabl scan . --no-rules-update   # offline: use cached rules, never reach out
```
