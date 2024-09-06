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
# interference_predictor.py

def predict_interference(angles):
    score = 0
    for angle_name, angle in angles.items():
        if 0 <= angle <= 10 or 170 <= angle <= 180:
            score += 10  # High score for conjunctions and oppositions
        elif 80 <= angle <= 100:
            score += 7  # Moderate score for squares (90°)
        elif 110 <= angle <= 130 or 50 <= angle <= 70:
            score -= 5  # Low score for trines (120°) and sextiles (60°)

    # Convert score to a probability
    probability = min(100, max(0, score * 1.5))  # Example scaling factor
    return score, probability
