# CLI reference

```
trustabl scan <target> [flags]   scan a local path or a remote repo URL
trustabl rules pull              download/refresh the rule packs into the cache
trustabl rules validate [dir]    validate a local rule-pack directory against this build
trustabl vulndb pull             pre-download the OSV vulnerability database
trustabl mcp                     run as a stdio MCP server (same scan, as an MCP tool)
trustabl enrich [flags]          add AI explanations/fixes to a scan result (BYOK)
trustabl llm ...                 configure the LLM provider/key/model for enrich
trustabl capabilities            print this build's rule-evaluation vocabulary as JSON
trustabl version                 print version, commit, and build date
```

Two **global** flags work on every subcommand and may appear before or after it
(`trustabl -v scan …` or `trustabl scan -v …`):

| Flag | Description |
|------|-------------|
| `--verbose`, `-v` | Narrate the scan on **stderr**: rule provenance, per-phase discovery counts, output destinations, and a result summary. |
| `--debug` | Everything `--verbose` shows, plus per-phase timing and per-entity / per-finding detail. Implies `--verbose`. |

Both write **only to stderr**, so they never perturb the report on stdout or the
JSON/SARIF byte-stability contract.

## `trustabl scan`

Scans `<target>` — a local path (directory or single file) or a GitHub URL
(`https://github.com/owner/repo`, optionally `.../tree/<ref>`). A remote target
is cloned read-only to a temp dir and removed on exit. The report is written to
stdout; progress, diagnostics, and warnings go to stderr.

| Flag | Default | Description |
|------|---------|-------------|
| `--detectors` | all | Comma-separated detector categories (see below). |
| `--format` | `human` | Output format: `human`, `json`, or `sarif`. |
| `--output`, `-o` | stdout | Write the report to a file instead of stdout (written before the findings-based exit code, so CI can upload it even on a failing scan). |
| `--json-out` | — | Also write the JSON `ScanResult` to this file, independent of `--format`. |
| `--sarif-out` | — | Also write the SARIF report to this file, independent of `--format`. |
| `--bom-out` | — | Also write a CycloneDX 1.5 BOM of the repo's declared dependencies to this file. |
| `--vuln-scan` | off | Match pinned dependencies against a pinned OSV snapshot and report known CVEs. Opt-in and online (fetches OSV on first use, then caches). |
| `--strict` | off | Exit `1` on any finding of **low** severity or higher (info/META signals never fail). |
| `--no-color` | off | Disable colored output. |
| `--rules-repo` | official | Rules repository URL (or set `TRUSTABL_RULES_REPO`). |
| `--rules-ref` | default branch | Rules branch or tag to use (branches and tags only, not raw SHAs). |
| `--channel` | — | Resolve rules from a signed release channel instead of git (opt-in, signature-verified; a pre-release channel is watermarked in the report). |
| `--no-rules-update` | off | Skip the network fetch; use the local cache only. |
| `--no-progress` | off | Disable real-time progress output. |

### Detector categories

`--detectors` accepts a comma-separated subset of:

```
claude_sdk   openai_sdk   google_adk   mcp        langchain
crewai       pydantic_ai  vercel_ai    autogen    claude_skill
openshell
```

!!! note
    `--detectors openshell` is accepted but currently selects zero rules — that
    pack moved to a closed-source companion project. OpenShell surfaces are still
    discovered and reported as a risk surface, just not rule-audited.

### Examples

```sh
# Restrict to specific SDKs
trustabl scan ./repo --detectors claude_sdk,mcp

# JSON to a file, plus a SARIF artifact, while the human panel prints to stdout
trustabl scan ./repo --json-out scan.json --sarif-out trustabl.sarif

# SARIF for a GitHub code-scanning upload
trustabl scan ./repo --format sarif -o trustabl.sarif

# Add a dependency CVE check and a CycloneDX BOM+VEX in one pass
trustabl scan ./repo --vuln-scan --bom-out bom.json

# Use a custom rules repository, pinned to a tag
trustabl scan ./repo --rules-repo https://github.com/org/my-rules --rules-ref v1.2.0

# Air-gapped: never touch the network, use cached rules
trustabl scan ./repo --no-rules-update
```

## `trustabl rules`

`trustabl rules pull` fetches the detection rule packs into the local cache
without running a scan. Honors `--rules-repo` / `TRUSTABL_RULES_REPO` and
`--rules-ref`.

```sh
trustabl rules pull
```

`trustabl rules validate [dir]` strict-loads every pack in a local rule-pack
directory against this build's schema and fails on the first error — the CI gate
the `trustabl-rules` repo runs on every change.

```sh
trustabl rules validate ./trustabl-rules
```

## `trustabl vulndb pull`

Pre-downloads the [OSV](https://osv.dev) vulnerability database into the local
cache, so a later `--vuln-scan` runs fully offline. `--vuln-scan` auto-fetches on
first use, so this is optional — useful to pre-warm the cache where you have
connectivity. The cache is reused until it is older than 24h; `--no-rules-update`
pins to the cache at any age.

```sh
trustabl vulndb pull
```

## `trustabl mcp`

Runs a Model Context Protocol server over stdio, so an MCP client (Claude Code,
Cursor, Claude Desktop) can scan a directory and read the findings back. It is
the same scan as `trustabl scan`, exposed as an MCP tool — it opens no network
port. JSON-RPC is on stdout; status and diagnostics go to stderr.

It exposes two tools:

- **`scan`** — input `{ "path": "<dir>", "rules_ref": "<branch-or-tag>"?, "vuln_scan": true? }`.
  Returns the full scan result (findings, scores, inventory) as JSON — the same
  shape as `--format json`. Set `vuln_scan: true` to also match dependencies
  against the OSV snapshot (off by default).
- **`version`** — reports the build version, commit, and date.

The rules-source flags (`--rules-repo`, `--rules-ref`, `--no-rules-update`) work
on `trustabl mcp` exactly as on `trustabl scan`; a per-call `rules_ref` overrides
the command-level `--rules-ref` for that call.

```sh
# Register with Claude Code
claude mcp add trustabl -- trustabl mcp
```

## `trustabl enrich`

Reads a `ScanResult` from `trustabl scan --format json` (via `--input` or stdin),
extracts the code around each flagged line, and asks Claude for code-specific
explanations and exact line replacements. Requires the active LLM provider to be
`anthropic` with a key set (see `trustabl llm`). The Anthropic call is the only
network call in the enrich path; `--apply` rewrites a file only when its current
contents still match what the model reviewed (writing a `.trustabl.bak` backup
first).

| Flag | Default | Description |
|------|---------|-------------|
| `--input`, `-i` | stdin | Path to the `ScanResult` JSON. |
| `--repo`, `-r` | `.` | Root of the scanned repository (for reading source). |
| `--output`, `-o` | stdout | Output file for the enriched JSON. |
| `--diff` | off | Print a unified diff of proposed replacements to stderr. |
| `--apply` | off | Write the fixes to source files; combine with `--diff` to preview first. |
| `--rule` | — | Filter to a specific rule ID (repeatable, e.g. `--rule CSDK-010`). |
| `--only-enriched` | off | Omit findings that could not be enriched. |

```sh
# Pipe a scan straight into enrich
trustabl scan ./repo --format json | trustabl enrich --repo ./repo

# Preview proposed fixes as a diff, then apply them
trustabl enrich --input scan.json --repo ./repo --diff --apply
```

## `trustabl llm`

Configures the LLM provider, API key, and model used by `trustabl enrich`. Keys
are stored at `~/.config/trustabl/keys.json` (mode 0600). The scan itself never
uses these — they are only for the opt-in enrich step.

```sh
trustabl llm list                       # configured providers, keys masked
trustabl llm key set                    # prompt securely for an API key
trustabl llm key set sk-ant-api03-...   # set non-interactively
trustabl llm key get                    # show masked key for active provider
trustabl llm key delete                 # delete key (with confirmation)
trustabl llm model set claude-sonnet-4-6  # change model for active provider
trustabl llm provider set anthropic     # switch active provider
trustabl llm provider list              # list configured providers
```

## `trustabl capabilities`

Prints this build's machine-readable capability descriptor as JSON — the
rule-schema version and every scope, language, detector category, `applies_to`
value, and match predicate it can evaluate. This is the contract a rule pack is
checked against; the `trustabl-rules` CI gate uses it to decide whether a
proposed rule would run, be skipped (forward-compatible), or break a release. The
output is deterministic (sorted).

```sh
trustabl capabilities > capabilities.json
```

## `trustabl version`

Prints the version, commit, and build date compiled into the binary.

## Exit codes

| Code | Meaning |
|------|---------|
| `0`  | No findings at or above medium severity. |
| `1`  | Findings ≥ medium present, or any finding ≥ low under `--strict` (info/META signals never raise the exit code). |
| `2`  | Scanner / I/O error; no usable rules available; or a signed `--channel` that failed verification. |

## The rule cache

Rules are cached under your OS cache directory (`os.UserCacheDir()`), keyed by
the resolved commit SHA. Trustabl fetches the configured ref, caches the clone,
and falls back to the cache when the network is unreachable — but a missing,
incompatible, *and* unfetchable rule set is a hard exit `2`: the engine never
runs rule-less and never reports a falsely clean result.

Rules load **forward-compatibly**: if the resolved pack targets a newer
rule-schema version than your binary understands, the scan still runs — it
evaluates every rule it can and skips the rest, warning on stderr and recording a
`META-005` info finding so a degraded scan is never mistaken for a clean one. To
evaluate the skipped rules, upgrade Trustabl or pin an older `--rules-ref`.
