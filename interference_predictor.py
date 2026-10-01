'''
Planetary Magnetic Interference Prediction System - scores pairwise heliocentric
planet angles using J.H. Nelson's aspect principles.
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
#
# The weights, orbs and scaling below were chosen by hand and have not been fitted
# to any geomagnetic or radio record. "Probability" is a rescaled score clamped to
# 0-100, not a calibrated probability.
import numpy as np


def predict_interference(angles):
    # Angles may be scalars or numpy arrays of equal shape (one value per instant)
    score = 0
    for angle_name, angle in angles.items():
        angle = np.asarray(angle)
        score = score + np.select(
            [
                ((0 <= angle) & (angle <= 10)) | ((170 <= angle) & (angle <= 180)),
                (80 <= angle) & (angle <= 100),
                ((110 <= angle) & (angle <= 130)) | ((50 <= angle) & (angle <= 70)),
            ],
            [
                10,  # High score for conjunctions and oppositions
                7,   # Moderate score for squares (90°)
                -5,  # Low score for trines (120°) and sextiles (60°)
            ],
            default=0
        )

    # Convert score to a 0-100 index
    probability = np.clip(score * 1.5, 0, 100)  # Example scaling factor
    if np.ndim(score) == 0:
        return int(score), float(probability)
    return score, probability
