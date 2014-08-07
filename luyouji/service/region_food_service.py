# encoding: utf-8
# Created on 2014-7-28
# @author: binge
from service import BaseService
from utils import settings

class RegionFoodService(BaseService):

    def __init__(self):
        BaseService.__init__(self, settings.mongo_region_food_collections_name)
