"""
This file holds common data for curiosity monitoring

"""

import os

CURIOSITY_ROVER_MISSION_URL = "https://mars.nasa.gov/msl/mission/where-is-the-rover/"
CURIOSITY_JSON = os.path.join("monitoring", "curiosity", "fixtures", "curiosity_rover_data.json")
CURIOSITY_WAYPOINT_MODEL = 'curiosity.curiositywaypoint'
CURIOSITY_MISSION_MODEL = 'curiosity.currentmission'
