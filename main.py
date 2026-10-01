'''
Planetary Magnetic Interference Prediction System - scores the heliocentric planet
configuration at one date and time, with optional CSV output and polar plot.
Copyright (C) 2024 William Blair

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

main.py

python main.py --date "1859-09-01" --time "11:18" --zone 0 --no_graphic
python main.py --date "1859-09-01" --time "11:18" --zone 0 --csv_output results.csv
python main.py --date "2024-07-04" --time "12:00" --zone America/New_York --no_graphic
python main.py --date "0044-03-15 BCE" --time "12:00" --zone 0 --no_graphic
'''
import argparse
import csv
import os
import re
import stat
import tempfile
import warnings
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import numpy as np

from astro_utils import (PLANET_IDENTIFIERS, date_to_jdn, get_all_angles, get_planet_positions,
                         is_valid_date, jdn_to_date, make_utc_time)
from interference_predictor import predict_interference

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

CSV_HEADER = (['Date', 'Time', 'Zone', 'UTC', 'Score', 'Probability']
              + [f'{planet}_RA' for planet in PLANET_IDENTIFIERS]
              + [f'{planet}_Dec' for planet in PLANET_IDENTIFIERS])


def parse_date(date_str, time_str):
    '''
    Parse "YYYY-MM-DD" (CE) or "YYYY-MM-DD BCE" plus "HH:MM".

    Returns (year, month, day, hour, minute) with an astronomical year, so
    1 BCE is year 0 and 44 BCE is year -43. Dates before 1582-10-15 are read
    in the Julian calendar. Raises ValueError for anything that isn't a real date.
    '''
    date_match = re.fullmatch(r'\s*([0-9]{1,4})-([0-9]{1,2})-([0-9]{1,2})\s*(BCE|CE)?\s*', date_str, re.IGNORECASE)
    if not date_match:
        raise ValueError(f"date '{date_str}' is not YYYY-MM-DD or YYYY-MM-DD BCE")
    time_match = re.fullmatch(r'\s*([0-9]{1,2}):([0-9]{2})\s*', time_str)
    if not time_match:
        raise ValueError(f"time '{time_str}' is not HH:MM")

    year, month, day = (int(part) for part in date_match.group(1, 2, 3))
    hour, minute = (int(part) for part in time_match.group(1, 2))
    if year == 0:
        raise ValueError("there is no year 0; use '0001-MM-DD BCE' for 1 BCE")
    if (date_match.group(4) or '').upper() == 'BCE':
        year = 1 - year
    if not is_valid_date(year, month, day):
        raise ValueError(f"{date_str} does not exist in the Julian/Gregorian calendar")
    if hour > 23 or minute > 59:
        raise ValueError(f"time '{time_str}' is out of range")
    return year, month, day, hour, minute


def parse_zone(zone_str):
    '''
    Parse a fixed UTC offset in hours ("-5", "5.5", "+05:30") or an IANA zone
    name ("America/New_York"). Returns a function giving the offset in minutes
    for a local (year, month, day, hour, minute).
    '''
    offset_match = re.fullmatch(r'\s*([+-]?)([0-9]{1,2})(?::([0-9]{2})|(\.[0-9]+))?\s*', zone_str)
    if offset_match:
        sign = -1 if offset_match.group(1) == '-' else 1
        minutes = int(offset_match.group(2)) * 60
        if offset_match.group(3):
            if int(offset_match.group(3)) > 59:
                raise ValueError(f"zone offset '{zone_str}' has more than 59 minutes")
            minutes += int(offset_match.group(3))
        elif offset_match.group(4):
            minutes += round(float(offset_match.group(4)) * 60)
        if minutes > 14 * 60:
            raise ValueError(f"zone offset '{zone_str}' is beyond ±14 hours")
        return lambda year, month, day, hour, minute: sign * minutes

    try:
        zone = ZoneInfo(zone_str)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError(f"zone '{zone_str}' is neither an hour offset nor an IANA time zone name")

    def iana_offset(year, month, day, hour, minute):
        # datetime is proleptic Gregorian, so it can't stand in for Julian-calendar dates
        if year < 1583:
            raise ValueError("IANA zones are only supported from 1583 on; use a numeric --zone offset")
        local = datetime(year, month, day, hour, minute, tzinfo=zone)
        return round(local.utcoffset().total_seconds() / 60)

    return iana_offset


def format_date(year, month, day):
    # Astronomical year back to historical CE/BCE labelling
    if year <= 0:
        return f"{1 - year:04d}-{month:02d}-{day:02d} BCE"
    return f"{year:04d}-{month:02d}-{day:02d}"


def local_to_utc(year, month, day, hour, minute, offset_minutes):
    # Exact integer conversion, so labels never suffer floating-point rounding
    total = date_to_jdn(year, month, day) * 1440 + hour * 60 + minute - offset_minutes
    jdn, minute_of_day = divmod(total, 1440)
    return (*jdn_to_date(jdn), minute_of_day // 60, minute_of_day % 60)


def compute(instants, zone_str):
    '''
    Score a list of local (year, month, day, hour, minute) instants in one
    vectorised pass. Returns (rows, planet_positions, angles), where rows follow
    CSV_HEADER and positions/angles hold one array element per instant.
    '''
    offset = parse_zone(zone_str)
    utc = [local_to_utc(*instant, offset(*instant)) for instant in instants]
    components = np.array(utc).T
    t = make_utc_time(*components)

    planet_positions = get_planet_positions(t)
    angles = get_all_angles(planet_positions)
    scores, probabilities = predict_interference(angles)
    scores, probabilities = np.atleast_1d(scores), np.atleast_1d(probabilities)

    rows = []
    for i, ((year, month, day, hour, minute), utc_instant) in enumerate(zip(instants, utc)):
        utc_label = f"{format_date(*utc_instant[:3])} {utc_instant[3]:02d}:{utc_instant[4]:02d}"
        row = [format_date(year, month, day), f"{hour:02d}:{minute:02d}", zone_str, utc_label,
               int(scores[i]), round(float(probabilities[i]), 2)]
        row += [round(float(np.atleast_1d(planet_positions[p]['ra'])[i]), 2) for p in PLANET_IDENTIFIERS]
        row += [round(float(np.atleast_1d(planet_positions[p]['dec'])[i]), 2) for p in PLANET_IDENTIFIERS]
        rows.append(row)
    return rows, planet_positions, angles


def write_csv(path, rows, append=False):
    if append and os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, newline='') as file:
            existing_header = next(csv.reader(file), None)
        if existing_header != CSV_HEADER:
            raise ValueError(f"{path} has a different column layout; write to a new file instead")
        with open(path, mode='a', newline='') as file:
            csv.writer(file).writerows(rows)
        return

    # Write to a temporary file and rename, so an interrupted run never leaves a partial CSV.
    # Resolve symlinks so the link target is replaced, not the link itself.
    path = os.path.realpath(path)
    if os.path.exists(path):
        mode = stat.S_IMODE(os.stat(path).st_mode)
    else:
        umask = os.umask(0)
        os.umask(umask)
        mode = 0o666 & ~umask
    with tempfile.NamedTemporaryFile('w', newline='', dir=os.path.dirname(path), delete=False, suffix='.tmp') as file:
        try:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER)
            writer.writerows(rows)
        except BaseException:
            file.close()
            os.unlink(file.name)
            raise
    try:
        os.chmod(file.name, mode)  # NamedTemporaryFile is created 0600
        os.replace(file.name, path)
    except BaseException:
        os.unlink(file.name)
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Score the heliocentric planet configuration at a date and time using "
                    "J.H. Nelson's aspect principles (uncalibrated index, 0-100).")
    parser.add_argument("--date", required=True, help='Date as YYYY-MM-DD, or "YYYY-MM-DD BCE"; '
                                                       'Julian calendar before 1582-10-15')
    parser.add_argument("--time", required=True, help="Local time as HH:MM")
    parser.add_argument("--zone", required=True,
                        help='UTC offset in hours ("-5", "5.5", "+05:30"; write --zone=-03:30 for a negative HH:MM) '
                             'or IANA name ("America/New_York")')
    parser.add_argument("--no_graphic", action="store_true", help="Disable graphics")
    parser.add_argument("--csv_output", help="CSV output file")
    parser.add_argument("--append", action="store_true", help="Append to CSV file if exists")

    args = parser.parse_args()

    try:
        instant = parse_date(args.date, args.time)
        rows, planet_positions, angles = compute([instant], args.zone)
    except ValueError as e:
        parser.error(str(e))

    row = rows[0]
    score, probability = row[4], row[5]
    print(f"Converted UTC Time: {row[3]}")
    print(f"Score: {score}")
    print(f"Probability of magnetic interference (uncalibrated index): {probability}%")

    if args.csv_output:
        try:
            write_csv(args.csv_output, rows, append=args.append)
        except ValueError as e:
            parser.error(str(e))
        print(f"Results {'appended to' if args.append else 'saved to'} {args.csv_output}")

    if not args.no_graphic:
        from visualization import plot_planet_positions_polar
        scalar_positions = {planet: {key: float(np.atleast_1d(value)[0]) for key, value in position.items()}
                            for planet, position in planet_positions.items()}
        plot_planet_positions_polar(scalar_positions, score, probability, row[0], row[1])


if __name__ == "__main__":
    main()
