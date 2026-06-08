# Quick start

After [installing](installation.md), scanning a repo is one command.

## Scan a local repo

```sh
trustabl scan ./path/to/agent-repo
```

Trustabl walks the repo, builds its inventory of agents and tools, runs the
applicable rule packs, and prints a human-readable report to stdout. Real-time
progress (recon → inventory → analysis) is shown on stderr — animated on a
terminal, plain `[phase] summary` lines when piped — and never pollutes the
report itself.

## Scan a remote repo

```sh
trustabl scan https://github.com/org/repo
```

The repo is shallow-cloned to a temporary directory and removed when the scan
exits. Nothing is written into the target repo, local or remote.

## Read the result

The report lists each finding with its rule ID, severity, the file and line (or
the agent/tool it attributes to), an explanation of *why* it matters, and a
suggested fix. A per-tool and overall reliability score summarizes the repo.

## Exit codes

Trustabl is built to gate CI. The process exit code encodes the outcome:

| Code | Meaning |
|------|---------|
| `0`  | No findings at or above **medium** severity. |
| `1`  | At least one finding ≥ medium (or any finding of **low** severity or higher under `--strict`; info/META signals never fail the build). |
| `2`  | Scanner / I/O error, or no usable rules were available. |

## Common variations

```sh
# JSON for CI piping
trustabl scan ./repo --format json

# SARIF for GitHub Code Scanning
trustabl scan ./repo --format sarif > trustabl.sarif

# Fail on any finding regardless of severity
trustabl scan ./repo --strict

# Only run one SDK's detectors
trustabl scan ./repo --detectors claude_sdk

# Also check dependencies for known CVEs (opt-in, uses the OSV database)
trustabl scan ./repo --vuln-scan

# Export a CycloneDX SBOM of declared dependencies (pure inventory)
trustabl scan ./repo --bom-out sbom.json
```

See the [CLI reference](cli-reference.md) for every flag, and
[Output formats](output-formats.md) for the JSON and SARIF shapes.
