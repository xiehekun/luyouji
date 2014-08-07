#coding:utf-8
# encoding: utf-8
# Created on 2014-5-23
# @author: binge

import pymongo
import traceback
import settings

def get_mongo():
    return pymongo.Connection(settings.mongo_host, settings.mongo_port)

def close_mongo(mongo):
    if mongo:
        mongo.close()

def mongo_exec(mongo):
    def wrapper(fn):
        def _exec(*args, **kwargs):
            try:
                return fn(mongo = mongo, *args, **kwargs)
            except:
                raise Exception(traceback.format_exc())
            finally:
                close_mongo(mongo)
        return _exec
    return wrapper

