# trustabl-docs

Source for the Trustabl documentation site, published with
[MkDocs Material](https://squidfunk.github.io/mkdocs-material/) to GitHub Pages.

The site **aggregates** content from the project's repos — it is not the source
of truth for any document it shows:

- **Hand-written pages** (overview, installation, quick start, use cases, output
  formats, CLI reference) live in [`docs/`](docs/) here.
- **Pulled pages** (architecture, coverage, the rule index and per-rule
  rationale) are copied in at build time from
  [`trustabl/trustabl`](https://github.com/trustabl/trustabl) and
  [`trustabl/trustabl-rulebook`](https://github.com/trustabl/trustabl-rulebook)
  by [`scripts/gather.py`](scripts/gather.py). Those repos remain authoritative;
  the pulled files are gitignored and never committed here.

## Preview locally

You need the sibling source repos checked out as `../trustabl` and
`../trustabl-rulebook` (or set `TRUSTABL_ENGINE_DIR` / `TRUSTABL_RULEBOOK_DIR`).

```sh
python -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
python scripts/gather.py        # copy pulled content into docs/
mkdocs serve                    # http://127.0.0.1:8000
```

## How it deploys

[`.github/workflows/docs.yml`](.github/workflows/docs.yml) runs on every push to
`main`: it checks out the source repos, runs `gather.py`, builds the site, and
deploys to GitHub Pages. Enable Pages for this repo with **Settings → Pages →
Build and deployment → Source: GitHub Actions**.

The published URL is `https://trustabl.github.io/trustabl-docs/` until a custom
domain (e.g. `docs.trustabl.<tld>`) is attached, which is a DNS `CNAME` plus the
Pages custom-domain setting — no rebuild required.
