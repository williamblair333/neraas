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

#astro_utils.py
'''
from skyfield.api import load
import numpy as np

def get_planet_positions(date):
    #planets = load('de421.bsp')  # Load planetary ephemeris small date range
    planets = load('de406.bsp')  # Load planetary ephemeris large date range 3000 BCE - 3000 CE
    ts = load.timescale()
    t = ts.utc(date.year, date.month, date.day, date.hour, date.minute)

    sun = planets['sun']

    # Correct names for planets in de406.bsp
    planet_identifiers = {
        'mercury': 'mercury',
        'venus': 'venus',
        'earth': 'earth',
        'mars': 'mars',
        'jupiter': 'jupiter barycenter',
        'saturn': 'saturn barycenter'
    }

    # Include the Sun at position (0, 0) in the heliocentric model
    planet_positions = {'sun': (0, 0, 0)}  # Sun at the origin

    for planet_name, planet_identifier in planet_identifiers.items():
        planet = planets[planet_identifier]
        astrometric = planet.at(t).observe(sun)
        ra, dec, distance = astrometric.radec()

        # Convert RA from hours to degrees (since RA is usually expressed in hours)
        ra_degrees = ra.hours * 15
        planet_positions[planet_name] = (ra_degrees, dec.degrees, distance.au)  # Add distance in Astronomical Units (AU)

    return planet_positions





def calculate_angle(ra1, dec1, ra2, dec2):
    # Convert angles to radians
    ra1, dec1, ra2, dec2 = map(np.radians, [ra1, dec1, ra2, dec2])

    # Calculate the angular separation
    delta_ra = ra2 - ra1
    angle = np.arccos(np.sin(dec1) * np.sin(dec2) + np.cos(dec1) * np.cos(dec2) * np.cos(delta_ra))
    return np.degrees(angle)

def get_all_angles(planet_positions):
    angles = {}
    planets = list(planet_positions.keys())
    for i in range(len(planets)):
        for j in range(i+1, len(planets)):
            angle = calculate_angle(
                planet_positions[planets[i]][0], planet_positions[planets[i]][1],
                planet_positions[planets[j]][0], planet_positions[planets[j]][1]
            )
            angles[f'{planets[i]}-{planets[j]}'] = angle
    return angles
