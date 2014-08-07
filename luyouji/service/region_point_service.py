# encoding: utf-8
# Created on 2014-7-28
# @author: binge
import service
from utils import settings

class RegionPointService():

    def __init__(self):
        self.region_sight_service = service.region_sight_serv
        self.region_food_service = service.region_food_serv
        self.region_shopping_service = service.region_shopping_serv

    def find(self, _type, conditions={}, sort=[('_id', 1)], skip=0, limit=-1):
        if settings.region_point_sight == _type:
            return self.region_sight_service.find(conditions, sort, skip, limit)
        if settings.region_point_food == _type:
            return self.region_food_service.find(conditions, sort, skip, limit)
        if settings.region_point_shopping == _type:
            return self.region_shopping_service.find(conditions, sort, skip, limit)
        return None

    def find_one(self, _type, conditions={}):
        if settings.region_point_sight == _type:
            return self.region_sight_service.find_one(conditions)
        if settings.region_point_food == _type:
            return self.region_food_service.find_one(conditions)
        if settings.region_point_shopping == _type:
            return self.region_shopping_service.find_one(conditions)
        return None
