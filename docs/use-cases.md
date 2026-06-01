# Use cases

Trustabl is a **read-only** static analyzer: it inspects agent code without
running it and without writing anything into the repo (remote targets are
shallow-cloned to a temp dir and removed on exit). Every scenario below is built
on the shipped feature set — SDK discovery, the four-scope rule engine, the
deterministic report, and the JSON / SARIF outputs.

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
