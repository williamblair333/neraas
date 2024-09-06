'''
Planetary Magnetic Interference Prediction System - A brief description of what the program does.
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

python main.py --date "1859-09-01" --time "11:55" --zone -5 --no_graphic
python main.py --date "1859-09-01" --time "11:55" --zone -5 --csv_output results.csv
python main.py --date "1859-09-01" --time "11:55" --zone -5 --no_graphic --csv_output results.csv
'''
import warnings
from datetime import datetime, timedelta
import argparse
import csv

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

# Ensure required modules are installed
from module_check_install import check_required_modules
check_required_modules()

from visualization import plot_planet_positions_polar
from astro_utils import get_planet_positions, get_all_angles
from interference_predictor import predict_interference

# Function to handle parsing of dates, including BCE dates
def parse_date(date_str, time_str):
    if "BCE" in date_str:
        year_str, month_day_str = date_str.split("-")[0], date_str[5:10]
        year = -int(year_str)
        date_str = f"{abs(year):04d}-{month_day_str}"
    return datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')

def main():
    parser = argparse.ArgumentParser(description="Your program description")
    parser.add_argument("--date", required=True, help="Date in the format YYYY-MM-DD")
    parser.add_argument("--time", required=True, help="Time in the format HH:MM")
    parser.add_argument("--zone", required=True, type=int, help="Time zone offset from UTC")
    parser.add_argument("--no_graphic", action="store_true", help="Disable graphics")
    parser.add_argument("--csv_output", help="CSV output file")
    parser.add_argument("--append", action="store_true", help="Append to CSV file if exists")

    args = parser.parse_args()

    # Combine date and time using the custom parse_date function
    try:
        user_datetime = parse_date(args.date, args.time)
    except ValueError as e:
        print(f"Error parsing date and time: {e}")
        return

    timezone_offset = timedelta(hours=args.zone)
    utc_datetime = user_datetime - timezone_offset

    print(f"Converted UTC Time: {utc_datetime.strftime('%Y-%m-%d %H:%M')}")

    # Step 1: Get planet positions
    planet_positions = get_planet_positions(utc_datetime)

    # Prepare RA and Dec info for display
    ra_dec_info = {planet: (ra, dec) for planet, (ra, dec, distance) in planet_positions.items()}

    # Step 2: Predict interference
    angles = get_all_angles(planet_positions)
    score, probability = predict_interference(angles)

    print(f"Score: {score}")
    print(f"Probability of magnetic interference: {probability}%")

    # Step 3: Save results to CSV if requested
    if args.csv_output:
        mode = 'a' if args.append else 'w'
        with open(args.csv_output, mode=mode, newline='') as file:
            writer = csv.writer(file)
            if not args.append or file.tell() == 0:  # Write header if not appending or file is empty
                headers = ['Date', 'Time', 'Score', 'Probability']
                headers += [f'{planet}_RA' for planet in ra_dec_info.keys()]
                headers += [f'{planet}_Dec' for planet in ra_dec_info.keys()]
                writer.writerow(headers)

            data = [args.date, args.time, score, probability]
            data += [round(ra, 2) for ra, _ in ra_dec_info.values()]
            data += [round(dec, 2) for _, dec in ra_dec_info.values()]
            writer.writerow(data)
        print(f"Results {'appended to' if args.append else 'saved to'} {args.csv_output}")

    # Step 4: Plot planetary positions if not disabled
    if not args.no_graphic:
        plot_planet_positions_polar(planet_positions, score, probability, ra_dec_info, args.date, args.time)

if __name__ == "__main__":
    main()
