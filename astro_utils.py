'''
Planetary Magnetic Interference Prediction System - heliocentric planet positions,
calendar arithmetic and pairwise angles.
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

#astro_utils.py

Years are astronomical: 1 BCE is year 0, 2 BCE is year -1.
Dates before 1582-10-15 are in the Julian calendar, later dates in the Gregorian.
'''
from functools import lru_cache

import numpy as np
from skyfield.api import load, GREGORIAN_START
from skyfield.framelib import ecliptic_J2000_frame

EPHEMERIS = 'de406.bsp'  # Planetary ephemeris covering 3000 BCE - 3000 CE

# Names for planets in de406.bsp
PLANET_IDENTIFIERS = {
    'mercury': 'mercury',
    'venus': 'venus',
    'earth': 'earth',
    'mars': 'mars',
    'jupiter': 'jupiter barycenter',
    'saturn': 'saturn barycenter'
}

# Julian Day Number of 1582-10-15, the first Gregorian date
GREGORIAN_START_JDN = 2299161


@lru_cache(maxsize=None)
def load_ephemeris():
    # Downloaded into the working directory on first use if not already present
    return load(EPHEMERIS)


@lru_cache(maxsize=None)
def get_timescale():
    ts = load.timescale()
    ts.julian_calendar_cutoff = GREGORIAN_START
    return ts


def date_to_jdn(year, month, day):
    # Julian Day Number, Julian calendar before 1582-10-15 and Gregorian from then on
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    if (year, month, day) >= (1582, 10, 15):
        return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083


def jdn_to_date(jdn):
    # Inverse of date_to_jdn
    if jdn >= GREGORIAN_START_JDN:
        a = jdn + 32044
        b = (4 * a + 3) // 146097
        c = a - 146097 * b // 4
    else:
        b = 0
        c = jdn + 32082
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10
    return year, month, day


def is_valid_date(year, month, day):
    # Rejects Feb 30, Feb 29 in common years and the 1582-10-05..14 gap
    if not 1 <= month <= 12 or not 1 <= day <= 31:
        return False
    return jdn_to_date(date_to_jdn(year, month, day)) == (year, month, day)


def make_utc_time(year, month, day, hour, minute):
    # Accepts scalars or numpy arrays; out-of-range minutes roll over into hours and days
    return get_timescale().utc(year, month, day, hour, minute)


def get_planet_positions(t):
    '''
    Heliocentric position of each planet at Skyfield Time t (scalar or array).

    Returns {planet: {'ra', 'dec', 'lon', 'lat', 'distance'}} with RA/Dec in the
    ICRS (J2000 equatorial) frame and lon/lat on the J2000 ecliptic, all in degrees,
    and distance in AU. Positions are geometric, measured from the Sun to the planet.
    The Sun itself is the origin, so it has no direction and is not included.
    '''
    planets = load_ephemeris()
    sun = planets['sun']

    planet_positions = {}
    for planet_name, planet_identifier in PLANET_IDENTIFIERS.items():
        heliocentric = (planets[planet_identifier] - sun).at(t)
        ra, dec, distance = heliocentric.radec()
        lat, lon, _ = heliocentric.frame_latlon(ecliptic_J2000_frame)
        planet_positions[planet_name] = {
            'ra': ra.hours * 15,  # RA is expressed in hours
            'dec': dec.degrees,
            'lon': lon.degrees,
            'lat': lat.degrees,
            'distance': distance.au
        }

    return planet_positions


def calculate_angle(ra1, dec1, ra2, dec2):
    # Convert angles to radians
    ra1, dec1, ra2, dec2 = map(np.radians, [ra1, dec1, ra2, dec2])

    # Angular separation via atan2, which stays accurate near 0° and 180°
    # where arccos of a rounded dot product can return NaN
    delta_ra = ra2 - ra1
    numerator = np.hypot(
        np.cos(dec2) * np.sin(delta_ra),
        np.cos(dec1) * np.sin(dec2) - np.sin(dec1) * np.cos(dec2) * np.cos(delta_ra)
    )
    denominator = np.sin(dec1) * np.sin(dec2) + np.cos(dec1) * np.cos(dec2) * np.cos(delta_ra)
    return np.degrees(np.arctan2(numerator, denominator))


def get_all_angles(planet_positions):
    angles = {}
    planets = list(planet_positions.keys())
    for i in range(len(planets)):
        for j in range(i+1, len(planets)):
            first, second = planet_positions[planets[i]], planet_positions[planets[j]]
            angle = calculate_angle(first['ra'], first['dec'], second['ra'], second['dec'])
            angles[f'{planets[i]}-{planets[j]}'] = angle
    return angles
