# encoding: utf-8
# Created on 2014-5-23
# @author: binge

import pymongo
from utils.settings import *  # @UnusedWildImport
import traceback
import redis
from pymongo import read_preferences

def get_mongo(doc_clz):
    return pymongo.Connection(mongo_host, mongo_port, read_preference=read_preferences.ReadPreference.PRIMARY, document_class=doc_clz)

def close_mongo(mongo):
    if mongo:
        mongo.close()

def mongo_exec(doc_clz=dict):
    def wrapper(fn):
        def _exec(*args, **kwargs):
            mongo = None
            try:
                mongo = get_mongo(doc_clz)
                return fn(mongo = mongo, *args, **kwargs)
            except:
                raise Exception(traceback.format_exc())
            finally:
                close_mongo(mongo)
        return _exec
    return wrapper

def get_redis_conn(db=redis_def_db):
    return redis.Redis(host=redis_host, port=redis_port, db=db)

def close_redis_conn(rconn):
    if rconn:
        del rconn

def redis_exec(db=redis_def_db):
    def wrapper(fn):
        def _exec(*args, **kwargs):
            rconn = None
            try:
                rconn = get_redis_conn(db)
                return fn(rconn = rconn, *args, **kwargs)
            except:
                raise Exception(traceback.format_exc())
            finally:
                close_redis_conn(rconn)
        return _exec
    return wrapper
