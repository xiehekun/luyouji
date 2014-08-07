# encoding: utf-8
# Created on 2014-7-8
# @author: binge
from service import BaseService
from utils import settings

class RegionService(BaseService):

    def __init__(self):
        BaseService.__init__(self, settings.mongo_region_collections_name)

