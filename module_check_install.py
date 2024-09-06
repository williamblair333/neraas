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
# module_check_install.py
import subprocess
import sys

def install_and_import(package):
    try:
        # Try importing the package
        __import__(package)
    except ModuleNotFoundError:
        # If not found, install it using pip
        print(f"Module '{package}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_required_modules():
    required_modules = ['skyfield', 'numpy', 'matplotlib', 'pytz']
    for module in required_modules:
        install_and_import(module)
