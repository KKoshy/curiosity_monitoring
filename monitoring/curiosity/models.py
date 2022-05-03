"""
This file comprises of models for Curiosity Waypoint and Current Mission

"""
from django.db import models


class CuriosityWaypoint(models.Model):
    """
    Class for defining fields of CuriosityWaypoint

    """
    sol = models.CharField(max_length=20)

    longitude = models.CharField(max_length=100)
    latitude = models.CharField(max_length=100)

    easting = models.CharField(max_length=100)
    northing = models.CharField(max_length=100)
    x_relative_to_waypoint = models.CharField(max_length=100)
    y_relative_to_waypoint = models.CharField(max_length=100)

    def __str__(self):
        return self.sol


class CurrentMission(models.Model):
    """
    Class for defining fields of CurrentMission

    """
    sol = models.CharField(max_length=20)
    target = models.CharField(max_length=20)
    distance_driven_in_miles = models.CharField(max_length=20)
    distance_driven_in_km = models.CharField(max_length=20)
    waypoints_count = models.IntegerField()
    visible_waypoints_count = models.IntegerField()

    def __str__(self):
        return self.target
