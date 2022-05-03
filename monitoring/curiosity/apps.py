"""
This file comprises of configurations for the graphql API

"""
from django.apps import AppConfig


class CuriosityConfig(AppConfig):
    """
    Class for configuring Curiosity graphql APIs

    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring.curiosity'
