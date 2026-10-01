'''
Planetary Magnetic Interference Prediction System - polar plan view of the
planets around the Sun.
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
'''
# visualization.py
import matplotlib.pyplot as plt
import numpy as np

def plot_planet_positions_polar(planet_positions, score, probability, date, time):
    # Set up a polar plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, polar=True)

    # Define the alchemical colors and symbols
    alchemical_colors = {
        'sun': 'gold',
        'mercury': 'gray',
        'venus': 'green',
        'earth': 'blue',
        'mars': 'red',
        'jupiter': 'orange',
        'saturn': 'black'
    }

    alchemical_symbols = {
        'sun': '☉',
        'mercury': '☿',
        'venus': '♀',
        'earth': '♁',
        'mars': '♂',
        'jupiter': '♃',
        'saturn': '♄'
    }

    # The Sun is the origin of the heliocentric frame
    ax.scatter(0, 0, label=f"{alchemical_symbols['sun']} Sun (0 AU)", color=alchemical_colors['sun'], s=200, edgecolor='black')

    for planet, position in planet_positions.items():
        # Ecliptic longitude as angle (theta) and distance as radius (r)
        lon_radians = np.radians(position['lon'])
        distance = position['distance']

        ax.scatter(lon_radians, distance, label=f"{alchemical_symbols[planet]} {planet.capitalize()} ({distance:.2f} AU)", color=alchemical_colors[planet], s=100)

        # Adjust the horizontal alignment and position of the labels
        ax.text(lon_radians, distance, planet, fontsize=9, ha='left', color=alchemical_colors[planet], va='bottom')

    # Plan view seen from the north ecliptic pole: longitude increases counter-clockwise from 0° at the right
    ax.set_title(f"Heliocentric Planet Positions (J2000 ecliptic longitude)\nDate: {date}, Time: {time}")
    ax.set_theta_direction(1)
    ax.set_theta_offset(0)

    # Move the legend outside the plot
    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)

    # Add another text box for additional information
    info_text = f"Score: {score}\nInterference index (uncalibrated): {probability}%\n\nHeliocentric J2000 RA & Dec:\n"
    for planet, position in planet_positions.items():
        info_text += f"{alchemical_symbols[planet]} {planet.capitalize()}: RA = {position['ra']:.2f}°, Dec = {position['dec']:.2f}°\n"

    # Anchored at the bottom so it sits below the legend instead of over it
    plt.gcf().text(0.78, 0.08, info_text, fontsize=10, va='bottom', bbox=dict(facecolor='white', alpha=0.5))

    # Show the plot
    plt.show()
