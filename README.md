# Planetary Magnetic Interference Prediction System (Inspired by J.H. Nelson's Work)

This project predicts potential magnetic interference by analyzing planetary positions and configurations, as inspired by the research of J.H. Nelson. Nelson's work in predicting radio interference through planetary configurations has been adapted into this computational model to anticipate magnetic disturbances.

## Features

- Predicts interference based on planetary positions and angles.
- Outputs graphical visualizations of planetary positions relative to the Sun.
- Generates detailed CSV reports of interference probabilities.
- Processes data across large date ranges, including BCE and CE.
- Supports interval-based data generation for comprehensive studies.
- Utilizes Nelson's principle of configurations: conjunctions (0°), oppositions (180°), and squares (90°).

## Requirements

The following Python packages are required:

skyfield
numpy
matplotlib
pytz

These can be installed automatically via the module_check_install.py script.

### Installation

To install the necessary dependencies and ensure all modules are available, run:

```bash python module_check_install.py```

### Usage
Basic Usage

Run the main script with a specific date and time to get the magnetic interference prediction:

```bash python main.py --date "YYYY-MM-DD" --time "HH:MM" --zone TIMEZONE_OFFSET ```

#### Example:

```bash python main.py --date "1859-09-01" --time "11:55" --zone -5 ```

### Options

    --no_graphic: Disable graphical output.
    --csv_output FILE: Save results to a CSV file.
    --append: Append data to an existing CSV file.

#### Generate Data in Intervals

To generate data for an extended period at specific intervals:

```bash python generate_data.py --start_year YEAR --end_year YEAR --interval INTERVAL --csv_output FILE ```

Available intervals: minutes, hours, days, months, seasons, years.


### Parallel Processing

Enable parallel processing for faster data generation with --parallel.

### Predictive Algorithm

    Planetary Positions: The system calculates the right ascension (RA) and declination (Dec) of planets using the skyfield library.
    Interference Prediction: Based on planetary configurations (angles of 0°, 90°, 180°), a score is calculated which translates to a probability of magnetic interference.
    Data Output: Results are outputted in both graphical (polar plots) and CSV format, showing planetary positions and predicted interference scores.

### Visualization

Polar plots can be generated showing the positions of the Sun and planets, with additional data on RA, Dec, and interference probability.

#### Example

To generate a CSV file with data for the year 1859:

```bash python generate_data.py --start_year 1859 --end_year 1859 --interval days --csv_output results.csv ```

### License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](./LICENSE) file for details.
