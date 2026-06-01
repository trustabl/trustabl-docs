# Output formats

Trustabl writes its report to **stdout**; progress and warnings go to
**stderr**. That separation is deliberate — stdout stays machine-clean so JSON
and SARIF consumers never see a stray progress line. Select the format with
`--format`.

## Human (default)

```sh
trustabl scan ./repo
# or explicitly
trustabl scan ./repo --format human
```

A readable summary: discovered inventory, each finding (rule ID, severity,
location, explanation, suggested fix), and per-tool plus overall reliability
scores. Use `--no-color` to disable ANSI styling.

## JSON

```sh
trustabl scan ./repo --format json
```

The full `ScanResult` as indented JSON — every field the engine produces:
the inventory, findings, scores, the resolved rules version, and a `coverage`
object reporting how many source files were parsed versus skipped (so an
incomplete scan is never mistaken for a clean one). Selecting `json` forces
progress output off.

## SARIF

```sh
trustabl scan ./repo --format sarif > trustabl.sarif
```

SARIF 2.1.0, accepted by `github/codeql-action/upload-sarif` and other
SARIF-aware tools. Results are sorted deterministically, severities map to SARIF
levels, and findings carry stable fingerprints so GitHub Code Scanning can
deduplicate alerts across runs.

## Determinism

Regardless of format or progress mode, the report is **byte-stable**: identical
inputs produce an identical `ScanID` — which folds in the resolved rules SHA, so
the ID is honest about which rule pack produced the scan — and identical output
bytes. This is enforced by a regression test in the engine.
