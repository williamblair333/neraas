# Changelog

## 2026-10-01 — Fix errors found by external review; add tests; ignore review folders

### Fixed
- `astro_utils.py`: positions were the antipode (`planet.at(t).observe(sun)`); now heliocentric `(planet - sun).at(t)`, matching Swiss Ephemeris to 0.01°.
- `astro_utils.py`: removed the `'sun': (0, 0, 0)` placeholder from the angle set; 6 of 21 pairs were planet-to-equinox angles. The score now uses 15 planet pairs, so scores differ from earlier runs.
- `astro_utils.py`: angle via `atan2`, so it can't return NaN at 0°/180°.
- `main.py`: "YYYY-MM-DD BCE" was computed as CE. Now astronomical years (1 BCE = 0), Julian calendar before 1582-10-15, and nonexistent dates are rejected.
- `generate_data.py`: `minutes`/`hours`/`days` intervals never terminated and produced invalid dates; the CSV collected only error messages. Rewritten as one vectorised process with an atomic CSV write.
- Errors now exit with code 2 instead of 0.

### Changed
- `--zone` accepts decimal and `HH:MM` offsets and IANA names (`--zone=-03:30` for a negative `HH:MM`). `generate_data.py` defaults to UTC instead of a hard-coded -5.
- CSV schema: added `Zone` and `UTC`; removed `sun_RA`/`sun_Dec`. `--append` refuses a file with a different layout.
- Plot uses J2000 ecliptic longitude, counter-clockwise, as a plan view from the north ecliptic pole.
- `module_check_install.py` (pip install at import) removed; pinned `requirements.txt` added (Python 3.12+).
- README corrected: uncalibrated index, coordinate frames, BCE handling, install steps, Carrington example time.
- `results.csv` regenerated.

### Added
- `tests/test_neraas.py` (52 tests; ephemeris tests skip when `de406.bsp` is absent).
- `.gitignore`: `/review/`, `/reviewed/`, `*.bsp`.
