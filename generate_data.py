'''
Planetary Magnetic Interference Prediction System - scores every instant across a
range of years at a fixed interval and writes them to one CSV file.
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

#Example command
python generate_data.py --start_year 2024 --end_year 2025 --interval months --csv_output results.csv; cat results.csv
'''

import argparse
import sys
from itertools import islice

from astro_utils import date_to_jdn, jdn_to_date
from main import compute, write_csv

FIXED_STEP_MINUTES = {"minutes": 1, "hours": 60, "days": 1440}
CALENDAR_MONTHS = {"months": range(1, 13), "seasons": (1, 4, 7, 10), "years": (1,)}
CHUNK_SIZE = 20000  # Instants computed per vectorised ephemeris call


def to_astronomical_year(year):
    # Historical numbering (-1000 = 1000 BCE, no year 0) to astronomical (1 BCE = 0)
    if year == 0:
        raise ValueError("there is no year 0; use -1 for 1 BCE")
    return year if year > 0 else year + 1


def generate_instants(start_year, end_year, interval):
    '''
    Yield local (year, month, day, hour, minute) instants from 1 January of
    start_year through 31 December of end_year, with astronomical years and real
    month lengths (Julian calendar before 1582-10-15, Gregorian after).
    '''
    first, last = to_astronomical_year(start_year), to_astronomical_year(end_year)
    if first > last:
        raise ValueError("start_year is after end_year")

    if interval in FIXED_STEP_MINUTES:
        start = date_to_jdn(first, 1, 1) * 1440
        stop = date_to_jdn(last + 1, 1, 1) * 1440
        for total in range(start, stop, FIXED_STEP_MINUTES[interval]):
            jdn, minute_of_day = divmod(total, 1440)
            yield (*jdn_to_date(jdn), minute_of_day // 60, minute_of_day % 60)
    else:
        for year in range(first, last + 1):
            for month in CALENDAR_MONTHS[interval]:
                yield year, month, 1, 0, 0


def generate_rows(instants, zone):
    instants = iter(instants)
    while chunk := list(islice(instants, CHUNK_SIZE)):
        rows, _, _ = compute(chunk, zone)
        yield from rows
        print(f"Computed up to {rows[-1][0]} {rows[-1][1]}", file=sys.stderr)


# Main function
def main():
    parser = argparse.ArgumentParser(description="Score planet configurations at fixed intervals and write them to a CSV file.")
    parser.add_argument("--start_year", type=int, required=True, help="Start year (e.g., -1000 for 1000 BCE; DE406 covers whole years -3000 to 2999)")
    parser.add_argument("--end_year", type=int, required=True, help="End year, inclusive (e.g., 2023)")
    parser.add_argument("--interval", type=str, required=True, choices=["minutes", "hours", "days", "months", "seasons", "years"], help="Interval type (minutes, hours, days, months, seasons, years)")
    parser.add_argument("--csv_output", required=True, help="CSV output file name")
    parser.add_argument("--zone", default="0", help='Zone the instants are local to: UTC offset in hours (write --zone=-03:30 for a negative HH:MM) or IANA name (default: UTC)')
    parser.add_argument("--append", action="store_true", help="Append to an existing CSV file instead of replacing it")
    parser.add_argument("--parallel", action="store_true", help="No effect; computation is vectorised. Kept so old commands still run")

    args = parser.parse_args()

    for year in (args.start_year, args.end_year):
        if not -3000 <= year <= 2999:
            parser.error(f"year {year} is outside the DE406 ephemeris range (whole years -3000 to 2999)")

    try:
        instants = generate_instants(args.start_year, args.end_year, args.interval)
        write_csv(args.csv_output, generate_rows(instants, args.zone), append=args.append)
    except ValueError as e:
        parser.error(str(e))

if __name__ == "__main__":
    main()
