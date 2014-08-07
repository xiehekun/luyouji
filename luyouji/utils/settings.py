# encoding: utf-8
# Created on 2014-5-23
# @author: binge

# mongo_host = '117.121.26.60'
mongo_host = '127.0.0.1'
mongo_port = 27017

redis_host = '127.0.0.1'
redis_port = 6379
redis_def_db = 0
redis_sep = ':::'

SESSION_MAXLIFETIME = 30 * 60
SESSION_REDIS_DB = 1

mongo_user_collections_name = 'users'
mongo_plan_collections_name = 'plans'
mongo_plan_detail_collections_name = 'plan_details'
mongo_country_collections_name = 'country'
mongo_region_collections_name = 'region'
mongo_region_sight_collections_name = 'region_sight'
mongo_region_food_collections_name = 'region_food'
mongo_region_shopping_collections_name = 'region_shopping'


default_user_source = 0
default_user_source_key = '0'

plan_day_detail_dest_type_sys = 0
plan_day_detail_dest_type_cus = 1

region_point_sight = 'sight'
region_point_food = 'food'
region_point_shopping = 'shopping'


qiqiu_access_key = 'uO7RwFu7ysNl55TmEoZedA-71XnAhihxCTZYEaG0'
qiqiu_secret_key = 'LaFc881Wp_f4TPfe0QkQGEVWbfCbYCu7VkuO-nCH'
qiqiu_bucket_name = 'luyouji'
qiqiu_img_url_prefix = 'http://luyouji.qiniudn.com/'

point_img_prefix = 'http://127.0.0.1/'
server_domain = 'http://192.168.1.13:8888'

reset_code_redis_prefix = 'reset_code_'
