"""
This file comprises of definitions for allWayPoints and currentMissionInfo queries

"""
import graphene
from graphene_django import DjangoObjectType

from monitoring.curiosity.models import CuriosityWaypoint, CurrentMission


class CuriosityWaypointType(DjangoObjectType):
    """
    Class for transforming CuriosityWaypoint Django model into object type

    """
    class Meta:
        model = CuriosityWaypoint
        fields = "__all__"


class CurrentMissionType(DjangoObjectType):
    """
    Class for transforming CurrentMission Django model into object type

    """
    class Meta:
        model = CurrentMission
        fields = "__all__"


class Query(graphene.ObjectType):
    """
    Class for adding graphql query objects

    """
    all_way_points = graphene.List(CuriosityWaypointType)
    current_mission_info = graphene.List(CurrentMissionType)

    def resolve_all_way_points(self, info):
        return CuriosityWaypoint.objects.all()

    def resolve_current_mission_info(self, info):
        return CurrentMission.objects.all()


schema = graphene.Schema(query=Query)
