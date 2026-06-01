#!/usr/bin/env python3
"""Aggregate documentation from the sibling Trustabl repos into docs/.

The docs site is an aggregator: canonical markdown lives in the engine
(trustabl) and rulebook (trustabl-rulebook) repos and is copied in here at
build time. The source repos stay the single source of truth — nothing is
forked or hand-duplicated. Edit ARCHITECTURE.md in the engine repo and the
site picks it up on the next build.

Source resolution, per repo, in order:
  1. $TRUSTABL_ENGINE_DIR / $TRUSTABL_RULEBOOK_DIR (explicit override)
  2. ./_src/<repo>            (where CI checks the repos out)
  3. ../<repo>               (sibling working copy, for local dev)

Run before `mkdocs build` / `mkdocs serve`:
    python scripts/gather.py
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


def resolve(repo: str, env_var: str) -> Path | None:
    candidates = []
    if os.environ.get(env_var):
        candidates.append(Path(os.environ[env_var]))
    candidates.append(ROOT / "_src" / repo)
    candidates.append(ROOT.parent / repo)
    for c in candidates:
        if c.is_dir():
            return c
    return None


def copy_file(src: Path, dst: Path, title: str | None = None) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    text = src.read_text(encoding="utf-8")
    if title:
        # Front matter sets the nav/title without editing the source file.
        text = f"---\ntitle: {title}\n---\n\n" + text
    dst.write_text(text, encoding="utf-8")
    print(f"  + {dst.relative_to(ROOT)}  <-  {src}")


def copy_tree(src: Path, dst: Path) -> int:
    n = 0
    for f in sorted(src.rglob("*.md")):
        rel = f.relative_to(src)
        out = dst / rel
        copy_file(f, out)
        n += 1
    return n


def main() -> int:
    engine = resolve("trustabl", "TRUSTABL_ENGINE_DIR")
    rulebook = resolve("trustabl-rulebook", "TRUSTABL_RULEBOOK_DIR")

    missing = []
    if engine is None:
        missing.append("trustabl (engine)")
    if rulebook is None:
        missing.append("trustabl-rulebook")
    if missing:
        print(
            "gather.py: could not locate source repo(s): "
            + ", ".join(missing)
            + "\nClone them as siblings (../<repo>), into ./_src/<repo>, or set "
            "TRUSTABL_ENGINE_DIR / TRUSTABL_RULEBOOK_DIR.",
            file=sys.stderr,
        )
        return 1

    print("Gathering docs from source repos:")
    print(f"  engine   = {engine}")
    print(f"  rulebook = {rulebook}")

    # Engine: detection mechanics + coverage matrix.
    copy_file(engine / "ARCHITECTURE.md", DOCS / "how-it-works" / "architecture.md",
              title="Architecture")
    copy_file(engine / "COVERAGE.md", DOCS / "coverage.md", title="Coverage")

    # Brand assets — binary, copied verbatim (never run through copy_file, which
    # treats content as text). Canonical home is the engine repo.
    #   logo_white.png — white mark for the teal header
    #   logo.png       — colored mark for the favicon (visible on light tabs)
    for asset in ("logo_white.png", "logo.png"):
        src = engine / "assets" / asset
        if src.is_file():
            dst = DOCS / "assets" / asset
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  + {dst.relative_to(ROOT)}  <-  {src}")

    # Rulebook: master rule index, per-SDK indexes, and per-rule rationale.
    # The master index links to <sdk>/POLICY_INDEX.md relative to itself, so the
    # per-SDK files are placed under rules/<sdk>/ to keep those links resolving.
    copy_file(rulebook / "POLICY_INDEX.md", DOCS / "rules" / "index.md",
              title="Rule index")
    for sdk in ("claude_sdk", "openai_sdk", "google_adk"):
        sdk_index = rulebook / sdk / "POLICY_INDEX.md"
        if sdk_index.is_file():
            copy_file(sdk_index, DOCS / "rules" / sdk / "POLICY_INDEX.md")
    policy_dir = rulebook / "docs" / "Policy"
    if policy_dir.is_dir():
        count = copy_tree(policy_dir, DOCS / "rules" / "rationale")
        print(f"  ({count} rationale pages)")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
