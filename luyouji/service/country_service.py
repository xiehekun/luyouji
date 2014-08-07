# encoding: utf-8
# Created on 2014-7-8
# @author: binge
from service import BaseService
from utils import settings

class CountryService(BaseService):

    def __init__(self):
        BaseService.__init__(self, settings.mongo_country_collections_name)

