"""
This file registers the models and displays them in the Django admin panel

"""
from django.contrib import admin

from .models import CurrentMission, CuriosityWaypoint

# Registering Current Mission and Curiosity Waypoint model
admin.site.register(CuriosityWaypoint)
admin.site.register(CurrentMission)
