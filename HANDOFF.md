# Handoff

## Current State (2026-10-01)

- `main` at the merge of PR #2 (Gitea http://localhost:3000/bill/neraas/pulls/2). Gitea push-mirrors to https://github.com/williamblair333/neraas automatically.
- All errors from the 2026-10-01 external review are fixed and tested (52 passing). The review is in `reviewed/2026-10-01-neraas-analysis.md`, which is gitignored and local only.
- Remotes: `origin` = Gitea (no `tea` CLI; PRs go through the REST API with `git credential fill`), `github` = direct GitHub remote for verification.

## Environment quirks

- `.venv/` (uv, Python 3.12) holds the deps plus `pytest` and `pyswisseph`. Run tests with `.venv/bin/python -m pytest tests -q`.
- `de406.bsp` in the repo root is a symlink to `/home/bill/Documents/github/neraas/de406.bsp` (ignored by `*.bsp`). Without it, skyfield downloads ~190 MB on first run.

## Not done (deliberately)

- Score weights, orbs and the ×1.5 "probability" are uncalibrated (review §3.6). Fitting them needs outcome data, e.g. GFZ Kp/ap since 1932, and a pre-registered test against a 27-day persistence baseline (review §7).
- Signed ecliptic-longitude differences are not logged. `lon`/`lat` are computed in `get_planet_positions` but aren't CSV columns.
- IANA zones silently resolve nonexistent or ambiguous DST local times; they use LMT before about 1883.
- `--append` is not atomic if generation fails partway.

## Next Session

- Most important: `/opt/proj/magicians-almanac/core/src/almanac_core/interference.py:45` is an adapted copy of neraas with the same 180° flip (`.observe(sun)`). Its pairwise angles are fine, but any absolute positions it reports are reversed. Decide whether to fix it there.
