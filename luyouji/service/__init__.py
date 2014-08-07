from utils import conns_helper

class BaseService():

    def __init__(self, collections_name):
        self.collections_name = collections_name

    @conns_helper.mongo_exec()
    def find(self, conditions={}, sort=[('_id', 1)], skip=0, limit=-1, **kwargs):
        collections = eval("kwargs['mongo'].luyou." + self.collections_name)
        if not limit == -1:
            cursor = collections.find(conditions).sort(sort).skip(skip).limit(limit)
        else:
            cursor = collections.find(conditions).sort(sort).skip(skip)
        docs = []
        for doc in cursor:
            docs.append(doc)
        return docs

    @conns_helper.mongo_exec()
    def find_all(self, **kwargs):
        collections = eval("kwargs['mongo'].luyou." + self.collections_name)
        docs = []
        cursor = collections.find()
        for doc in cursor:
            docs.append(doc)
        return docs

    @conns_helper.mongo_exec()
    def find_one(self, conditions={}, return_fields={}, **kwargs):
        collections = eval("kwargs['mongo'].luyou." + self.collections_name)
        return collections.find_one(conditions)

    @conns_helper.mongo_exec()
    def insert(self, doc, **kwargs):
        collections = eval("kwargs['mongo'].luyou." + self.collections_name)
        collections.insert(doc)
#         return self.find_one(self.collections_name, {'_id' : doc['_id']}, **kwargs)

    @conns_helper.mongo_exec()
    def find_page(self, curr_page, page_size, conditions={}, sort=[('_id', 1)], **kwargs):
        if not curr_page or curr_page < 1:
            curr_page = 1
        collections = eval("kwargs['mongo'].luyou." + self.collections_name)
        cursor = collections.find(conditions).sort(sort).skip((curr_page - 1) * page_size).limit(page_size * 2)
        page = {'curr_page' : curr_page}
        docs = []
        i = 0
        for doc in cursor:
            docs.append(doc)
            i += 1
            if i > page_size:
                page['next_page'] = curr_page + 1
                break
        docs = docs[:page_size]
        page['docs'] = docs
        if curr_page > 1:
            page['prev_page'] = curr_page - 1
        return page

    @conns_helper.mongo_exec()
    def update(self, conditions={}, update_doc=None, **kwargs):
        collections = eval("kwargs['mongo'].luyou." + self.collections_name)
        collections.update(conditions, update_doc)

    @conns_helper.mongo_exec()
    def remove(self, conditions={}, **kwargs):
        collections = eval("kwargs['mongo'].luyou." + self.collections_name)
        collections.remove(conditions)

from service.country_service import CountryService
from service.plan_detail_service import PlanDetailService
from service.plan_service import PlanService
from service.region_service import RegionService
from service.user_service import UserService
from service.region_sight_service import RegionSightService
from service.region_food_service import RegionFoodService
from service.region_shopping_service import RegionShoppingService
from service.region_point_service import RegionPointService
from service.images_service import ImagesService

country_serv = CountryService()
plan_detail_serv = PlanDetailService()
plan_serv = PlanService()
region_serv = RegionService()
user_serv = UserService()
region_sight_serv = RegionSightService()
region_food_serv = RegionFoodService()
region_shopping_serv = RegionShoppingService()
region_point_serv = RegionPointService()
imgs_serv = ImagesService()
