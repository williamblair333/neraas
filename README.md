# Planetary Magnetic Interference Prediction System (Inspired by J.H. Nelson's Work)

This project scores planetary configurations for potential magnetic interference, inspired by the research of J.H. Nelson. Nelson's work in predicting radio interference through planetary configurations has been adapted into this computational model.

The score is **uncalibrated**: its weights, orbs and scaling were chosen by hand and have not been fitted to, or tested against, any geomagnetic or radio record. The "probability" it reports is a 0–100 index derived from the score, not a calibrated probability.

## Features

- Scores heliocentric angles between every pair of planets (Mercury, Venus, Earth, Mars, Jupiter, Saturn).
- Outputs graphical visualizations of planetary positions relative to the Sun.
- Generates CSV reports of scores and heliocentric positions.
- Processes dates from 3000 BCE to 2999 CE, using the Julian calendar before 1582-10-15 and the Gregorian calendar after.
- Supports interval-based data generation for comprehensive studies.
- Uses Nelson's principle of configurations: conjunctions (0°), oppositions (180°) and squares (90°) raise the score; trines (120°) and sextiles (60°) lower it.

## Requirements

Python 3.12 or later (required by the pinned numpy) and the packages pinned in `requirements.txt` (skyfield, jplephem, numpy, matplotlib).

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On first run, skyfield downloads the JPL DE406 ephemeris (`de406.bsp`, about 190 MB) into the working directory.

### Usage

Run the main script with a specific date and time to get the magnetic interference score:

```bash
python main.py --date "YYYY-MM-DD" --time "HH:MM" --zone ZONE
```

`--zone` is a UTC offset in hours (`-5`, `5.5`, `+05:30`) or an IANA time zone name (`America/New_York`, which follows daylight saving time; supported from 1583 on). A negative offset in `HH:MM` form needs an equals sign, `--zone=-03:30`, or write it as `-3.5`.

BCE dates take a `BCE` suffix: `--date "0044-03-15 BCE"`. There is no year 0; 1 BCE is followed directly by 1 CE.

#### Example

The Carrington flare, observed at about 11:18 GMT on 1 September 1859:

```bash
python main.py --date "1859-09-01" --time "11:18" --zone 0
```

### Options

    --no_graphic: Disable graphical output.
    --csv_output FILE: Save results to a CSV file.
    --append: Append data to an existing CSV file (it must have the same columns).

#### Generate Data in Intervals

To generate data for an extended period at specific intervals:

```bash
python generate_data.py --start_year YEAR --end_year YEAR --interval INTERVAL --csv_output FILE [--zone ZONE] [--append]
```

Available intervals: minutes, hours, days, months, seasons, years. Years are inclusive; use negative years for BCE (`-1000` is 1000 BCE). Instants are local to `--zone`, which defaults to UTC.

All instants are computed in one process with the ephemeris loaded once, and the CSV is written in a single pass. A year at one-minute resolution (about 527,000 rows) takes tens of seconds. `--parallel` is still accepted but no longer has any effect.

### Predictive Algorithm

    Planetary Positions: Heliocentric (Sun-to-planet) geometric positions from the JPL DE406 ephemeris via the skyfield library.
    Interference Prediction: Each of the 15 planet pairs adds +10 for a conjunction or opposition (±10°), +7 for a square (±10°), and -5 for a trine or sextile (±10°). The index is the score × 1.5, clamped to 0–100.
    Angles: The angle for a pair is the full 3-D separation between the two heliocentric directions, which includes ecliptic latitude. It can differ by a few degrees from a difference of ecliptic longitudes, most for Mercury (7° orbital inclination), and it doesn't distinguish waxing from waning aspects.
    Data Output: Results are written as polar plots and CSV, showing planetary positions and interference scores.

### CSV Columns

    Date, Time, Zone: the local instant as given.
    UTC: the same instant in UTC.
    Score, Probability: the raw score and the 0–100 index.
    <planet>_RA, <planet>_Dec: heliocentric right ascension and declination in degrees, in the ICRS (J2000 equatorial) frame.

RA/Dec are J2000 equatorial coordinates, not ecliptic longitude, so they don't map directly onto zodiac signs (tropical or sidereal). The angles between planets, and therefore the score, are the same in every frame.

### Visualization

Polar plots show the planets around the Sun as seen from the north ecliptic pole: J2000 ecliptic longitude increases counter-clockwise from 0° at the right, and the radius is distance in AU.

#### Example

To generate a CSV file with one row per day for the year 1859:

```bash
python generate_data.py --start_year 1859 --end_year 1859 --interval days --csv_output results.csv
```

### Tests

```bash
pip install pytest
python -m pytest tests
```

Ephemeris-dependent tests are skipped when `de406.bsp` is not present.

### License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](./LICENSE) file for details.
