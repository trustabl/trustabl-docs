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
the inventory, findings, scores, the resolved rules version, a `coverage`
object reporting how many source files were parsed versus skipped (so an
incomplete scan is never mistaken for a clean one), and — when `--vuln-scan` is
on — a `vulnerabilities` array of matched dependency advisories. Selecting `json`
forces progress output off.

## SARIF

```sh
trustabl scan ./repo --format sarif > trustabl.sarif
```

SARIF 2.1.0, accepted by `github/codeql-action/upload-sarif` and other
SARIF-aware tools. Results are sorted deterministically, severities map to SARIF
levels, and findings carry stable fingerprints so GitHub Code Scanning can
deduplicate alerts across runs.

## Writing to a file

`--format` controls what goes to stdout; three flags write to files instead of
(or alongside) stdout:

```sh
# Write the report to a file in the chosen format (instead of stdout)
trustabl scan ./repo --format sarif --output trustabl.sarif

# One scan, human summary on stdout, both machine artifacts persisted
trustabl scan ./repo --json-out trustabl.json --sarif-out trustabl.sarif
```

`--output`/`-o` redirects the `--format` report to a file. `--json-out` and
`--sarif-out` write those formats to a file independent of `--format`, so a
single scan can print the human panel while persisting the JSON and SARIF. The
file bytes are identical to the matching `--format` stdout output, and `--output`
writes the file *before* the findings-based exit code is applied — so a CI step
can upload the report even when the scan exits `1` on findings.

## Dependency BOM (CycloneDX)

```sh
# Pure inventory of declared dependencies
trustabl scan ./repo --bom-out sbom.json

# BOM + VEX: add a vulnerabilities[] array from the OSV match
trustabl scan ./repo --vuln-scan --bom-out bom.json
```

`--bom-out` writes a byte-stable CycloneDX 1.5 BOM of the direct dependencies the
repo declares across every supported language — pip / npm / Go / Composer / NuGet
/ Cargo manifests. It is pure inventory and makes no network call. Combined with
`--vuln-scan`, the document is upgraded from a plain BOM into a **BOM plus VEX**:
the matched advisories are emitted as a CycloneDX `vulnerabilities[]` array, each
with the advisory ID, an OSV `source`, a severity `rating`, an upgrade
`recommendation`, and an `affects[]` reference to the component — a standards-based
artifact any CycloneDX-aware tool can ingest.

## Determinism

Regardless of format or progress mode, the report is **byte-stable**: identical
inputs produce an identical `ScanID` — which folds in the resolved rules SHA, so
the ID is honest about which rule pack produced the scan — and identical output
bytes. When `--vuln-scan` is on, the OSV snapshot version is folded into the
`ScanID` too, so the result is honest about which vulnerability data produced it;
a default scan stays byte-identical to before. This is enforced by a regression
test in the engine.
