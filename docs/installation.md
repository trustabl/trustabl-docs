# Installation

Trustabl is distributed as a single binary for macOS, Linux, and Windows. Pick
whichever channel fits your environment.

## Homebrew (macOS, Linux)

```sh
brew install trustabl/tap/trustabl
```

## Scoop (Windows)

```sh
scoop bucket add trustabl https://github.com/trustabl/scoop-bucket
scoop install trustabl
```

## Docker

The image is published to GitHub Container Registry. Mount the repo you want to
scan and point the scan at the mount:

```sh
docker run --rm -v "$PWD:/repo" ghcr.io/trustabl/trustabl:latest scan /repo
```

`:latest` tracks the most recent final release; pin a version tag
(`ghcr.io/trustabl/trustabl:0.1.0`) for reproducible CI.

## Direct download

Download the archive for your OS/arch from the
[GitHub Releases page](https://github.com/trustabl/trustabl/releases), extract
it, and put the `trustabl` binary on your `PATH`. Each archive also bundles
`LICENSE`, `README.md`, `COVERAGE.md`, and `CHANGELOG.md`. A `checksums.txt`
(SHA-256) and build-provenance attestation are published alongside the archives.

## Verify the install

```sh
trustabl version
```

This prints the version, commit, and build date baked into the binary.

## First run and the rule cache

On its first scan, Trustabl resolves the detection rule packs from the
[`trustabl-rules`](https://github.com/trustabl/trustabl-rules) repository and
caches them under your OS cache directory. Later scans reuse the cache and fall
back to it when the network is unreachable. To pre-warm the cache without
scanning:

```sh
trustabl rules pull
```

A scan with no usable rules (none cached and none fetchable) exits with code `2`
rather than reporting a misleadingly clean result.

The opt-in `--vuln-scan` dependency check keeps a separate cache: it fetches a
pinned [OSV](https://osv.dev) snapshot on first use and reuses it (offline-capable)
on later scans. Pre-warm it where you have connectivity with:

```sh
trustabl vulndb pull
```
