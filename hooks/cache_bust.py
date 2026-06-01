"""Cache-bust extra_css/extra_javascript by content hash.

MkDocs fingerprints the theme's own assets (main.<hash>.min.css) so a change
gets a new URL and browsers refetch it. It does NOT do this for user
extra_css / extra_javascript, so those keep a fixed name and get served stale
from cache after every edit. This hook appends a short content hash as a query
string (e.g. stylesheets/extra.css?h=ab12cd34); when the file's bytes change,
the hash changes, the URL changes, and the browser is forced to refetch — while
still caching aggressively when nothing changed.
"""

from __future__ import annotations

import hashlib
import os


def _digest(path: str) -> str | None:
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:8]


def _bust(entries: list[str], docs_dir: str) -> list[str]:
    out = []
    for entry in entries:
        # Only fingerprint local files (skip absolute URLs / already-versioned).
        if "://" in entry or "?" in entry:
            out.append(entry)
            continue
        h = _digest(os.path.join(docs_dir, entry.replace("/", os.sep)))
        out.append(f"{entry}?h={h}" if h else entry)
    return out


def on_config(config, **kwargs):
    docs_dir = config["docs_dir"]
    config["extra_css"] = _bust(list(config["extra_css"]), docs_dir)
    config["extra_javascript"] = _bust(list(config["extra_javascript"]), docs_dir)
    return config
