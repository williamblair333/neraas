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
'''
# visualization.py
import matplotlib.pyplot as plt
import numpy as np

def plot_planet_positions_polar(planet_positions, score, probability, ra_dec_info, date, time):
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

    for planet, (ra, dec, distance) in planet_positions.items():
        if planet == 'sun':  # Sun is at the center
            ax.scatter(0, 0, label=f"{alchemical_symbols[planet]} Sun (0 AU)", color=alchemical_colors[planet], s=200, edgecolor='black')
            continue

        # Convert RA (Right Ascension) to radians for the polar plot
        ra_radians = np.radians(ra)

        # Plot each planet with RA as angle (theta) and distance as radius (r)
        ax.scatter(ra_radians, distance, label=f"{alchemical_symbols[planet]} {planet.capitalize()} ({distance:.2f} AU)", color=alchemical_colors[planet], s=100)

        # Adjust the horizontal alignment and position of the labels
        ax.text(ra_radians, distance, planet, fontsize=9, ha='left', color=alchemical_colors[planet], va='bottom')

    # Labels and grid settings for the polar plot
    ax.set_title(f"Planetary Positions Relative to the Sun\nDate: {date}, Time: {time}")
    ax.set_theta_direction(-1)  # Set direction of theta (clockwise)
    ax.set_theta_offset(np.pi / 2.0)  # Set the zero-point to the top (as in celestial maps)

    # Move the legend outside the plot
    legend1 = ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)

    # Add another text box for additional information
    info_text = f"Score: {score}\nProbability of Magnetic Interference: {probability}%\n\nRA & Dec:\n"
    for planet, (ra, dec) in ra_dec_info.items():
        info_text += f"{alchemical_symbols[planet]} {planet.capitalize()}: RA = {ra:.2f}°, Dec = {dec:.2f}°\n"

    plt.gcf().text(0.78, 0.5, info_text, fontsize=10, bbox=dict(facecolor='white', alpha=0.5))

    # Show the plot
    plt.show()

