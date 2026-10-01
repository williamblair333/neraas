import csv
import os
import sys
from itertools import islice

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from astro_utils import (calculate_angle, date_to_jdn, get_all_angles, get_planet_positions,
                         is_valid_date, jdn_to_date, make_utc_time)
import generate_data
from generate_data import generate_instants, to_astronomical_year
from interference_predictor import predict_interference
from main import CSV_HEADER, compute, local_to_utc, parse_date, parse_zone, write_csv

needs_ephemeris = pytest.mark.skipif(
    not os.path.exists(os.path.join(ROOT, 'de406.bsp')),
    reason="de406.bsp not present (avoids a ~190 MB download during tests)")


@pytest.fixture(autouse=True)
def run_in_repo_root(monkeypatch):
    # load('de406.bsp') resolves against the working directory
    monkeypatch.chdir(ROOT)


# --- Calendar ---------------------------------------------------------------

def test_jdn_matches_known_values():
    assert date_to_jdn(2000, 1, 1) == 2451545
    assert date_to_jdn(1582, 10, 15) == 2299161
    assert date_to_jdn(1582, 10, 4) == 2299160  # Julian day before the Gregorian start
    assert date_to_jdn(-4712, 1, 1) == 0


@pytest.mark.parametrize("jdn", [0, 625360, 1705426, 2299160, 2299161, 2451545, 2817000])
def test_jdn_round_trip(jdn):
    assert date_to_jdn(*jdn_to_date(jdn)) == jdn


def test_valid_dates():
    assert is_valid_date(1500, 2, 29)        # Julian leap year
    assert not is_valid_date(1700, 2, 29)    # Gregorian common year
    assert is_valid_date(2024, 2, 29)
    assert not is_valid_date(2023, 2, 29)
    assert not is_valid_date(2024, 2, 30)
    assert not is_valid_date(1582, 10, 10)   # Dropped in the Gregorian switch
    assert is_valid_date(0, 2, 29)           # 1 BCE is a Julian leap year


# --- Date, time and zone parsing (review 3.3, 3.5) --------------------------

def test_bce_dates_use_astronomical_years():
    assert parse_date("0044-03-15 BCE", "12:00") == (-43, 3, 15, 12, 0)
    assert parse_date("0001-01-01 BCE", "00:00")[0] == 0
    assert parse_date("1859-09-01", "11:18") == (1859, 9, 1, 11, 18)


@pytest.mark.parametrize("date_str,time_str", [
    ("2023-02-29", "00:00"), ("2024-02-30", "00:00"), ("0000-01-01", "00:00"),
    ("1582-10-10", "00:00"), ("2024-01-01", "24:00"), ("01/01/2024", "00:00"),
])
def test_invalid_dates_raise(date_str, time_str):
    with pytest.raises(ValueError):
        parse_date(date_str, time_str)


@pytest.mark.parametrize("zone,minutes", [("-5", -300), ("5.5", 330), ("+05:30", 330), ("-3:30", -210), ("0", 0)])
def test_numeric_zones(zone, minutes):
    assert parse_zone(zone)(2024, 1, 1, 0, 0) == minutes


@pytest.mark.parametrize("zone", ["-5:60", "+5:99", "15", "５", "Not/AZone"])
def test_invalid_zones_raise(zone):
    with pytest.raises(ValueError):
        parse_zone(zone)


def test_unicode_digits_are_not_dates():
    with pytest.raises(ValueError):
        parse_date("２０２４-01-01", "00:00")


def test_iana_zone_follows_daylight_saving():
    zone = parse_zone("America/New_York")
    assert zone(2024, 1, 15, 12, 0) == -300
    assert zone(2024, 7, 15, 12, 0) == -240
    with pytest.raises(ValueError):
        zone(1500, 1, 1, 0, 0)


def test_local_to_utc_rolls_over_days_and_years():
    assert local_to_utc(2023, 12, 31, 22, 0, -300) == (2024, 1, 1, 3, 0)
    assert local_to_utc(2024, 1, 1, 2, 0, 330) == (2023, 12, 31, 20, 30)


# --- Interval generation (review 3.4) ----------------------------------------

@pytest.mark.parametrize("interval,year,count", [
    ("days", 2023, 365), ("days", 2024, 366), ("hours", 2024, 8784),
    ("minutes", 2023, 525600), ("months", 2024, 12), ("seasons", 2024, 4), ("years", 2024, 1),
    ("days", -1, 366),  # 1 BCE is a Julian leap year
    ("days", 1582, 355),  # Ten days dropped in October
])
def test_generated_intervals_terminate_with_real_month_lengths(interval, year, count):
    instants = list(generate_instants(year, year, interval))
    assert len(instants) == count
    assert all(is_valid_date(*instant[:3]) for instant in instants)
    assert all(instant[3] < 24 and instant[4] < 60 for instant in instants)


def test_generated_days_stay_in_order_across_years():
    instants = list(generate_instants(2023, 2024, "days"))
    assert instants[0] == (2023, 1, 1, 0, 0)
    assert instants[-1] == (2024, 12, 31, 0, 0)
    assert instants == sorted(instants)


def test_historical_year_conversion():
    assert to_astronomical_year(-1000) == -999
    assert to_astronomical_year(1) == 1
    with pytest.raises(ValueError):
        to_astronomical_year(0)


# --- Angles and score (review 3.2, 3.7) ---------------------------------------

def test_angle_of_identical_and_opposite_directions_is_not_nan():
    assert calculate_angle(123.4, 56.7, 123.4, 56.7) == pytest.approx(0.0, abs=1e-9)
    assert calculate_angle(10.0, 20.0, 190.0, -20.0) == pytest.approx(180.0, abs=1e-9)
    assert calculate_angle(0.0, 0.0, 90.0, 0.0) == pytest.approx(90.0)


def test_score_works_on_scalars_and_arrays():
    scalar = predict_interference({'a-b': 5.0, 'a-c': 90.0, 'b-c': 120.0})
    assert scalar == (12, 18.0)
    score, probability = predict_interference({'a-b': np.array([5.0, 60.0]), 'a-c': np.array([90.0, 175.0])})
    assert list(score) == [17, 5]
    assert list(probability) == [25.5, 7.5]


# --- Ephemeris (review 2, 3.1, 3.2) -------------------------------------------

@needs_ephemeris
def test_positions_point_from_sun_to_planet():
    # Heliocentric J2000 equatorial values from Swiss Ephemeris (pyswisseph 2.10,
    # FLG_HELCTR | FLG_EQUATORIAL | FLG_J2000) at 2024-01-01 05:00 UTC
    expected = {
        'mercury': (149.70, 19.75), 'venus': (187.18, 0.38), 'mars': (257.61, -23.86),
        'jupiter': (43.38, 15.47), 'saturn': (339.90, -10.34),
    }
    positions = get_planet_positions(make_utc_time(2024, 1, 1, 5, 0))
    for planet, (ra, dec) in expected.items():
        assert positions[planet]['ra'] == pytest.approx(ra, abs=0.03)
        assert positions[planet]['dec'] == pytest.approx(dec, abs=0.03)
    # Earth seen from the Sun is opposite the geocentric Sun (RA 280.79, Dec -23.07)
    assert positions['earth']['ra'] == pytest.approx(100.79, abs=0.03)
    assert positions['earth']['dec'] == pytest.approx(23.07, abs=0.03)


@needs_ephemeris
def test_sun_is_not_part_of_the_angle_set():
    angles = get_all_angles(get_planet_positions(make_utc_time(2024, 1, 1, 5, 0)))
    assert len(angles) == 15
    assert not any('sun' in pair for pair in angles)


@needs_ephemeris
def test_jupiter_saturn_trine_1954():
    angles = get_all_angles(get_planet_positions(make_utc_time(1954, 6, 24, 0, 0)))
    assert float(angles['jupiter-saturn']) == pytest.approx(120.0, abs=0.1)


@needs_ephemeris
def test_vectorised_compute_matches_single_instants():
    instants = list(islice(generate_instants(2024, 2024, "months"), 3))
    batch, _, _ = compute(instants, "-5")
    singles = [compute([instant], "-5")[0][0] for instant in instants]
    assert batch == singles
    assert batch[0][3] == "2024-01-01 05:00"


@needs_ephemeris
def test_chunked_rows_match_one_pass(monkeypatch):
    instants = list(generate_instants(2024, 2024, "days"))[:50]
    expected, _, _ = compute(instants, "0")
    monkeypatch.setattr(generate_data, "CHUNK_SIZE", 7)
    assert list(generate_data.generate_rows(instants, "0")) == expected


@needs_ephemeris
def test_bce_instant_computes_and_is_labelled_bce():
    rows, _, _ = compute([parse_date("0044-03-15 BCE", "12:00")], "0")
    assert rows[0][0] == "0044-03-15 BCE"
    assert rows[0][3] == "0044-03-15 BCE 12:00"


# --- CSV output (review 3.4) --------------------------------------------------

def test_write_csv_replaces_atomically_and_appends_with_matching_header(tmp_path):
    path = tmp_path / "out.csv"
    row = ["2024-01-01", "00:00", "0", "2024-01-01 00:00", 1, 1.5] + [0.0] * 12
    write_csv(str(path), [row])
    write_csv(str(path), [row], append=True)
    with open(path, newline='') as file:
        lines = list(csv.reader(file))
    assert lines[0] == CSV_HEADER
    assert len(lines) == 3
    assert list(tmp_path.iterdir()) == [path]  # No temporary file left behind


def test_write_csv_keeps_file_mode_and_replaces_symlink_target(tmp_path):
    target = tmp_path / "target.csv"
    target.write_text("old\n")
    os.chmod(target, 0o644)
    link = tmp_path / "link.csv"
    link.symlink_to(target)
    write_csv(str(link), [])
    assert link.is_symlink()
    assert oct(os.stat(target).st_mode & 0o777) == oct(0o644)
    assert target.read_text().startswith("Date,")


def test_write_csv_refuses_to_append_to_a_different_layout(tmp_path):
    path = tmp_path / "old.csv"
    path.write_text("Date,Time,Score,Probability,sun_RA\n")
    with pytest.raises(ValueError):
        write_csv(str(path), [], append=True)


def test_write_csv_leaves_no_partial_file_on_failure(tmp_path):
    path = tmp_path / "out.csv"

    def failing_rows():
        yield ["x"] * len(CSV_HEADER)
        raise ValueError("boom")

    with pytest.raises(ValueError):
        write_csv(str(path), failing_rows())
    assert list(tmp_path.iterdir()) == []
