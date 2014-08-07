# encoding: utf-8
# Created on 2014-7-8
# @author: binge
from service import BaseService
from utils import settings

class PlanService(BaseService):
    '''
    extends BaserService.
    '''
    def __init__(self):
        BaseService.__init__(self, settings.mongo_plan_collections_name)
