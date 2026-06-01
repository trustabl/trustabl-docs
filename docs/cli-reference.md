# CLI reference

```
trustabl scan <target> [flags]   scan a local path or a remote repo URL
trustabl rules pull [flags]      download/refresh the rule packs into the cache
trustabl version                 print version, commit, and build date
```

## `trustabl scan`

Scans `<target>` — a local directory or a remote repo URL (cloned read-only to a
temp dir, removed on exit).

| Flag | Default | Description |
|------|---------|-------------|
| `--detectors` | all | Comma-separated detector categories: `claude_sdk`, `openai_sdk`, `google_adk`, `openshell`. |
| `--format` | `human` | Output format: `human`, `json`, or `sarif`. |
| `--strict` | off | Exit `1` if **any** finding is present, regardless of severity. |
| `--no-color` | off | Disable colored output. |
| `--rules-repo` | official | Rules repository URL (or set `TRUSTABL_RULES_REPO`). |
| `--rules-ref` | default branch | Rules branch or tag to use. |
| `--no-rules-update` | off | Skip the network fetch; use the local cache only. |
| `--no-progress` | off | Disable real-time progress output. |

!!! note
    `--detectors openshell` is accepted but currently selects zero rules — that
    pack is maintained separately and not shipped in the public rule set.

### Examples

```sh
# Restrict to specific SDKs
trustabl scan ./repo --detectors claude_sdk,openai_sdk

# Use a custom rules repository, pinned to a tag
trustabl scan ./repo --rules-repo https://github.com/org/my-rules --rules-ref v1.2.0

# Air-gapped: never touch the network, use cached rules
trustabl scan ./repo --no-rules-update
```

## `trustabl rules pull`

Fetches the detection rule packs into the local cache without running a scan.
Honors `--rules-repo` / `TRUSTABL_RULES_REPO` and `--rules-ref`.

```sh
trustabl rules pull
```

## `trustabl version`

Prints the version, commit, and build date compiled into the binary.

## Exit codes

| Code | Meaning |
|------|---------|
| `0`  | No findings at or above medium severity. |
| `1`  | Findings ≥ medium present (or any finding under `--strict`). |
| `2`  | Scanner / I/O error, or no usable rules available. |

## The rule cache

Rules are cached under your OS cache directory (`os.UserCacheDir()`), keyed by
the resolved commit SHA. Trustabl fetches the configured ref, caches the clone,
and falls back to the cache when the network is unreachable — but a missing,
incompatible, *and* unfetchable rule set is a hard exit `2`: the engine never
runs rule-less and never reports a falsely clean result.
