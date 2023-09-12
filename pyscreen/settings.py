"""
All default settings for the ATC program.
Includes all Constants, default values, and other settings.
"""

import os
from typing import final

## get current directory
__dir__ = os.path.dirname(os.path.realpath(__file__))

## get parent directory
ROOT: final = os.path.dirname(__dir__)
MEDIA_ROOT: final = os.path.join(ROOT, "media")

# SuperSampling for Anti-Aliasing (AA) if AA is not supported by the SDL2 library
AASUPERSAMPLING = 4





# magic functions
def __getFontPath(fontName: str):
    return os.path.join(MEDIA_ROOT, "fonts", fontName)
FONT = __getFontPath

def __getImagePath(imageName: str):
    return os.path.join(MEDIA_ROOT, "images", imageName)
IMAGE = __getImagePath



# scale settings
LOC_DRAW_SCALE_RANGE = (5000, 150_000)
RWY_DRAW_SCALE_RANGE = (5000, 300_000)
MIN_WAYPOINT_SCALE = 150_000
MIN_SIMPLEWAYPOINT_SCALE = 20000
MIN_VOR_SCALE = 5000
MIN_TACAN_SCALE = 5000
MIN_AIRPORT_SCALE = 5000
MIN_NDB_SCALE = 15000
SHOW_FREQ_SCALE = 100000

MIN_SCALE = 200
MAX_SCALE = 2_000_000

MAX_LATITUDE = 70 # Do not use values too close to the poles, as the map projection will fail