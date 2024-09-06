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

#Example command
clear; rm *.csv; python generate_data.py --start_year 2024 --end_year 2025 --interval months --csv_output results.csv; cat results.csv
'''

import argparse
import subprocess
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import os

# Function to run the command and capture output
def run_command(date, time, output_file):
    command = [
        "python", "main.py",
        "--date", date,
        "--time", time,
        "--zone", "-5",
        "--no_graphic",
        "--csv_output", output_file,
        "--append"
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return date, time, result.stdout.strip()

# Function to generate dates based on interval type (manual for BCE dates)
def generate_dates(start_year, end_year, interval):
    current_year = start_year
    current_month = 1
    current_day = 1
    current_hour = 0
    current_minute = 0

    while current_year <= end_year:
        if current_year < 0:
            date = f"{abs(current_year):04d}-{current_month:02d}-{current_day:02d} BCE"
        else:
            date = f"{current_year:04d}-{current_month:02d}-{current_day:02d}"

        yield date, f"{current_hour:02d}:{current_minute:02d}"

        # Increment the date based on the interval
        current_year, current_month, current_day, current_hour, current_minute = increment_date(
            current_year, current_month, current_day, current_hour, current_minute, interval
        )

# Helper function to increment date manually
def increment_date(year, month, day, hour, minute, interval):
    if interval == "minutes":
        minute += 1
        if minute == 60:
            minute = 0
            hour += 1
    elif interval == "hours":
        hour += 1
        if hour == 24:
            hour = 0
            day += 1
    elif interval == "days":
        day += 1
        if day > 30:  # Simplified, adjust as needed for actual month length
            day = 1
            month += 1
    elif interval == "months":
        month += 1
        if month > 12:
            month = 1
            year += 1
    elif interval == "seasons":
        month += 3
        if month > 12:
            month = (month % 12)
            year += 1
    elif interval == "years":
        year += 1

    return year, month, day, hour, minute

# Helper function to write CSV header
def write_csv_header(csv_output):
    if not os.path.exists(csv_output):
        with open(csv_output, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            header = [
                'Date', 'Time', 'Score', 'Probability',
                'sun_RA', 'mercury_RA', 'venus_RA', 'earth_RA', 'mars_RA', 'jupiter_RA', 'saturn_RA',
                'sun_Dec', 'mercury_Dec', 'venus_Dec', 'earth_Dec', 'mars_Dec', 'jupiter_Dec', 'saturn_Dec'
            ]
            writer.writerow(header)

# Function to parse and clean the output
def clean_output(output):
    if "Score:" in output or "Converted UTC Time:" in output:
        return None  # Filter out unwanted log messages
    return output.strip() if isinstance(output, str) else None

# Function to convert BCE/CE date to sortable tuple (year, month, day)
def parse_bce_ce_date(date_str):
    if "BCE" in date_str:
        year, month, day = date_str.split(" ")[0].split("-")
        year = -int(year)  # Convert BCE year to negative
    else:
        year, month, day = date_str.split("-")
        year = int(year)  # CE year remains positive
    return (year, int(month), int(day))

# Main function
def main():
    parser = argparse.ArgumentParser(description="Generate data in intervals.")
    parser.add_argument("--start_year", type=int, required=True, help="Start year (e.g., -1000 for 1000 BCE)")
    parser.add_argument("--end_year", type=int, required=True, help="End year (e.g., 2023)")
    parser.add_argument("--interval", type=str, required=True, choices=["minutes", "hours", "days", "months", "seasons", "years"], help="Interval type (minutes, hours, days, months, seasons, years)")
    parser.add_argument("--csv_output", required=True, help="CSV output file name")
    parser.add_argument("--parallel", action="store_true", help="Enable parallel processing (disabled by default)")

    args = parser.parse_args()

    # Write CSV header once
    write_csv_header(args.csv_output)

    # Initialize the results list
    results = []

    # Check if parallel processing is enabled
    if args.parallel:
        # Use parallel processing
        with ThreadPoolExecutor() as executor:
            future_to_date = {executor.submit(run_command, date, time, args.csv_output): (date, time)
                            for date, time in generate_dates(args.start_year, args.end_year, args.interval)}

            for future in as_completed(future_to_date):
                date, time = future_to_date[future]
                try:
                    result = future.result()
                    cleaned_result = clean_output(result[2])
                    if cleaned_result:
                        results.append((date, time, cleaned_result))
                except Exception as e:
                    print(f"Error processing date {date}: {e}")
    else:
        # Use sequential processing
        for date, time in generate_dates(args.start_year, args.end_year, args.interval):
            try:
                result = run_command(date, time, args.csv_output)
                cleaned_result = clean_output(result[2])
                if cleaned_result:
                    results.append((date, time, cleaned_result))
            except Exception as e:
                print(f"Error processing date {date}: {e}")

    # Sort results by date and time before writing
    results.sort(key=lambda x: (parse_bce_ce_date(x[0]), x[1]))

    # Append sorted results to CSV
    with open(args.csv_output, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for date, time, output in results:
            output_data = output.split(",")
            writer.writerow([date, time] + output_data)

if __name__ == "__main__":
    main()
