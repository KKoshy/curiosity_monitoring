"""
This script collects the visible waypoint data of curiosity from the map embedded in the
official website of NASA.
https://mars.nasa.gov/msl/mission/where-is-the-rover/

"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait as wait
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import re

CURIOSITY_ROVER_MISSION_URL = "https://mars.nasa.gov/msl/mission/where-is-the-rover/"
ROVER_MAP = '//iframe[@src="https://mars.nasa.gov/maps/location/?mission=MSL&site=NOW"]'
MISSION = 'topBarTitle'
WAYPOINTS = "path.waypoints.leaflet-interactive"
MOUSE_LONG_LAT = 'p#mouseLngLat'
POSITION_DATA = 'div.mouseLngLat'
SOL_VALUE = "mainDescPointInner"
CURRENT_ROVER_POSITION = 'img.leaflet-marker-icon.leaflet-zoom-animated.leaflet-interactive'
CURIOSITY_JSON = "curiosity_rover_data.json"


class CuriosityWaypoints:
    """
    Class to collect Curiosity Waypoint data

    """

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
        self.mission_data = []
        self.waypoints_count = 0

    def create_rover_json_data(self):
        """
        Creates a json file with the mission data
        :return: None

        """
        with open(CURIOSITY_JSON, "w") as wd:
            json.dump(self.mission_data, wd)

    def get_position_value(self, long_lat):
        """
        Extracts the value of position
        :param long_lat: web element of the position data
        :return: position value

        """
        long_lat.click()
        position_value = self.driver.find_element(By.CSS_SELECTOR, MOUSE_LONG_LAT)
        return position_value.text.split(", ")

    def get_waypoint_data(self, waypoint_data):
        """
        Collects longitude, latitude, easting, northing, relative x and
        relative y values of each waypoint
        :param waypoint_data: dictionary of waypoint data
        :return: updated waypoint_data

        """
        # Longitude and Latitude of waypoint
        long_lat = self.driver.find_element(By.CSS_SELECTOR, POSITION_DATA)
        wait(self.driver, 15).until(EC.element_to_be_clickable(long_lat))
        waypoint_data['longitude'], waypoint_data['latitude'] = self.get_position_value(long_lat)

        # Easting and Northing of waypoint
        waypoint_data['easting'], waypoint_data['northing'] = self.get_position_value(long_lat)

        # Relative distance to waypoint
        waypoint_data['x_relative_to_waypoint'], waypoint_data['y_relative_to_waypoint'] = \
            self.get_position_value(long_lat)

        return waypoint_data

    def get_sol_value(self):
        """
        Gets the sol value for each waypoint
        :return: sol value

        """
        wait(self.driver, 10).until(EC.presence_of_element_located((By.ID, SOL_VALUE)))
        waypoint_id = self.driver.find_element(By.ID, SOL_VALUE)
        return re.search(r': (\d*)', waypoint_id.text).groups()[0]

    def get_current_position_data(self):
        """
        Gets the current position data of the rover
        :return: current_position_value

        """
        # adding current sol data
        wait(self.driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, CURRENT_ROVER_POSITION)))
        current_position = self.driver.find_element(By.CSS_SELECTOR, CURRENT_ROVER_POSITION)
        current_position.click()
        current_position_value = {'sol': self.get_sol_value()}
        current_position_value = self.get_waypoint_data(current_position_value)
        return current_position_value

    def traverse_visible_waypoints(self):
        """
        Traverses the visible waypoints of the rover map and collects position
        data of each waypoint
        :return: None

        """
        waypoints = self.driver.find_elements(By.CSS_SELECTOR, WAYPOINTS)
        self.waypoints_count = len(waypoints)
        for waypoint in waypoints:
            waypoint_data = {}
            if waypoint.is_displayed():
                try:
                    wait(self.driver, 15).until(EC.element_to_be_clickable(waypoint))
                    waypoint.click()

                    # Waypoint data collection
                    waypoint_data['sol'] = self.get_sol_value()
                    waypoint_data = self.get_waypoint_data(waypoint_data)
                    self.mission_data.append(waypoint_data)

                except ElementClickInterceptedException:
                    print("Skipping a waypoint")

        current_position_data = self.get_current_position_data()
        self.mission_data.append(current_position_data)

    def get_current_mission_info(self):
        """
        Gets the current mission info (target, sol, distance driven, etc.,)
        :return: None

        """
        # obtaining the title from the map -> Curiosity's Location
        cu_title = self.driver.find_element(By.ID, MISSION)
        mission_current_info = {"target": cu_title.text}

        # obtaining current sol data from the map
        sol_data = self.driver.find_element(By.CSS_SELECTOR, 'div.mainInfo').text
        sol = re.search(r'Sol (\d*) ', sol_data).groups()[0]
        mission_current_info["sol"] = sol

        # obtaining distance driven
        distance_driven_in_miles = re.search(r'Distance Driven (\d*.\d*) miles ', sol_data).groups()[0]
        mission_current_info["distance_driven_in_miles"] = distance_driven_in_miles

        distance_driven_in_km = re.search(r' (\d*.\d*) km', sol_data).groups()[0]
        mission_current_info["distance_driven_in_km"] = distance_driven_in_km

        # including total waypoints count
        mission_current_info["waypoints_count"] = self.waypoints_count

        self.mission_data.append(mission_current_info)

    def load_curiosity_rover_map(self):
        """
        Loads the mission url and switches to the rover map
        :return: None

        """
        self.driver.get(CURIOSITY_ROVER_MISSION_URL)

        # switching to the map iframe of curiosity
        iframe = self.driver.find_element(By.XPATH, ROVER_MAP)
        wait(self.driver, 15).until(EC.frame_to_be_available_and_switch_to_it(iframe))

    def collect_curiosity_data(self):
        """
        Drives the curiosity data collection
        :return: None

        """
        self.load_curiosity_rover_map()
        self.traverse_visible_waypoints()
        self.get_current_mission_info()
        self.create_rover_json_data()
        self.driver.quit()


if __name__ == "__main__":
    cw = CuriosityWaypoints()
    cw.collect_curiosity_data()
