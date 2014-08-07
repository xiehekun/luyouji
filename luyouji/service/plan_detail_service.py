# encoding: utf-8
# Created on 2014-7-8
# @author: binge
from service import BaseService
from utils import settings

class PlanDetailService(BaseService):
    '''
    extends BaseService.
    '''
    def __init__(self):
        BaseService.__init__(self, settings.mongo_plan_detail_collections_name)

    def init_details(self, p_id, details_days):
        for _id in details_days:
            self.insert({'_id' : _id, 'p_id' : p_id, 'day' : details_days[_id]})
