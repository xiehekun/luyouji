# encoding: utf-8
# Created on 2014-5-23
# @author: binge
from service import BaseService
from utils import settings


class UserService(BaseService):
    '''
    extends BaseService.
    '''

    def __init__(self):
        BaseService.__init__(self, settings.mongo_user_collections_name)

