"""
This script collects the visible waypoint data of curiosity from the map embedded in the
official website of NASA.
https://mars.nasa.gov/msl/mission/where-is-the-rover/

"""

import logging
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait as wait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from data.common import CURIOSITY_JSON, CURIOSITY_MISSION_MODEL, \
    CURIOSITY_WAYPOINT_MODEL, CURIOSITY_ROVER_MISSION_URL

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(processName)s '
                           '%(threadName)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)


class CuriosityWaypoints:
    """
    Class to collect Curiosity Waypoint data

    """
    ROVER_MAP = (By.XPATH,
                 '//iframe[@src="https://mars.nasa.gov/maps/location/?mission=MSL&site=NOW"]')
    MISSION = (By.ID, 'topBarTitle')
    WAYPOINTS = (By.XPATH,
                 "//*[name()='svg']/*[name()='g']/*[name()='path'][contains(@class, 'waypoints')]")
    MOUSE_LONG_LAT = (By.CSS_SELECTOR, 'p#mouseLngLat')
    POSITION_DATA = (By.CSS_SELECTOR, 'div.mouseLngLat')
    SOL_VALUE = (By.ID, "mainDescPointInner")
    CURRENT_ROVER_POSITION = (By.CSS_SELECTOR,
                              'img.leaflet-marker-icon.leaflet-zoom-animated.leaflet-interactive')

    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.mission_data = []
        self.waypoints_count = 0
        self.visible_waypoint_count = 0

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
        position_value = self.driver.find_element(*self.MOUSE_LONG_LAT)
        return position_value.text.split(", ")

    def get_waypoint_data(self):
        """
        Collects sol, longitude, latitude, easting, northing, relative x and
        relative y values of each waypoint
        :return: updated waypoint_data

        """
        # Sol of waypoint
        waypoint_data_fields = {'sol': self.get_sol_value()}

        # Longitude and Latitude of waypoint
        long_lat = self.driver.find_element(*self.POSITION_DATA)
        wait(self.driver, 15).until(EC.element_to_be_clickable(long_lat))
        waypoint_data_fields['longitude'], waypoint_data_fields['latitude'] = \
            self.get_position_value(long_lat)

        # Easting and Northing of waypoint
        waypoint_data_fields['easting'], waypoint_data_fields['northing'] = \
            self.get_position_value(long_lat)

        # Relative distance to waypoint
        waypoint_data_fields['x_relative_to_waypoint'], \
        waypoint_data_fields['y_relative_to_waypoint'] = self.get_position_value(long_lat)

        return waypoint_data_fields

    def get_sol_value(self):
        """
        Gets the sol value for each waypoint
        :return: sol value

        """
        wait(self.driver, 10).until(EC.presence_of_element_located(self.SOL_VALUE))
        waypoint_id = self.driver.find_element(*self.SOL_VALUE)
        return re.search(r': (\d*)', waypoint_id.text).groups()[0]

    def get_current_position_data(self):
        """
        Gets the current position data of the rover
        :return: current_position_value

        """
        # adding current sol data; commented to neglect.
        # wait(self.driver, 15).until(EC.element_to_be_clickable(self.CURRENT_ROVER_POSITION))
        # current_position = self.driver.find_element(*self.CURRENT_ROVER_POSITION)
        # current_position.click()
        current_position_value = {'model': CURIOSITY_WAYPOINT_MODEL, 'pk': self.get_sol_value(),
                                  'fields': self.get_waypoint_data()}
        return current_position_value

    def traverse_visible_waypoints(self):
        """
        Traverses the visible waypoints of the rover map and collects position
        data of each waypoint
        :return: None

        """
        logging.info("Traversing Waypoints available on the map")
        wait(self.driver, 15).until(EC.presence_of_element_located(self.WAYPOINTS))
        waypoints = self.driver.find_elements(*self.WAYPOINTS)
        self.waypoints_count = len(waypoints)
        for waypoint in waypoints:
            if waypoint.is_displayed():
                try:
                    wait(self.driver, 15).until(EC.element_to_be_clickable(waypoint))
                    waypoint.click()
                    self.visible_waypoint_count += 1
                    # Waypoint data collection
                    waypoint_data = {'model': CURIOSITY_WAYPOINT_MODEL,
                                     'pk': self.get_sol_value(),
                                     'fields': self.get_waypoint_data()}
                    self.mission_data.append(waypoint_data)
                except ElementClickInterceptedException:
                    print("Skipping a waypoint")

        current_position_data = self.get_current_position_data()
        self.mission_data.append(current_position_data)

    def get_current_mission_info(self):
        """
        Gets the current mission info (target, sol, distance driven, etc.,)
        :return: mission_current_info

        """
        # obtaining the title from the map -> Curiosity's Location
        cu_title = self.driver.find_element(*self.MISSION)
        mission_current_info = {"target": cu_title.text}

        # obtaining current sol data from the map
        sol_data = self.driver.find_element(By.CSS_SELECTOR, 'div.mainInfo').text
        sol = re.search(r'Sol (\d*) ', sol_data).groups()[0]
        mission_current_info["sol"] = sol

        # obtaining distance driven
        distance_driven_in_miles = \
            re.search(r'Distance Driven (\d*.\d*) miles ', sol_data).groups()[0]
        mission_current_info["distance_driven_in_miles"] = distance_driven_in_miles

        distance_driven_in_km = re.search(r' (\d*.\d*) km', sol_data).groups()[0]
        mission_current_info["distance_driven_in_km"] = distance_driven_in_km

        # including total waypoints count
        mission_current_info["waypoints_count"] = self.waypoints_count
        mission_current_info['visible_waypoints_count'] = self.visible_waypoint_count + 1

        return mission_current_info

    def load_curiosity_rover_map(self):
        """
        Loads the mission url and switches to the rover map
        :return: None

        """
        logging.info("Loading Curiosity Rover map")
        self.driver.get(CURIOSITY_ROVER_MISSION_URL)

        # switching to the map iframe of curiosity
        iframe = self.driver.find_element(*self.ROVER_MAP)
        wait(self.driver, 15).until(EC.frame_to_be_available_and_switch_to_it(iframe))

    def collect_curiosity_data(self):
        """
        Drives the curiosity data collection
        :return: None

        """
        self.load_curiosity_rover_map()
        self.traverse_visible_waypoints()
        current_mission_info = {'model': CURIOSITY_MISSION_MODEL, 'pk': 1,
                                'fields': self.get_current_mission_info()}
        self.mission_data.append(current_mission_info)
        self.create_rover_json_data()
        self.driver.quit()


if __name__ == "__main__":
    cw = CuriosityWaypoints()
    cw.collect_curiosity_data()
