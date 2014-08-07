# encoding: utf-8
# Created on 2014-5-27
# @author: binge

from hashlib import sha1
from tenjin.helpers import *
from tornado.web import RequestHandler, HTTPError
from utils import settings, conns_helper
from utils.common import TimeHelper
import json
import os
import tenjin
import time
import traceback
import uuid
import service
from tornado import log

tenjin_engine = tenjin.Engine(pp=[ tenjin.TrimPreprocessor() ], layout=os.path.join(os.path.dirname(__file__), "views/_layout.html"))

class BaseHandler(RequestHandler):

    MTHOD_NOT_ALLOWED = 405
    URL_NOT_FOUND = 404
    SERVER_ERROR = 500

    _skip_attrs = ['get', 'post']

    _redis = conns_helper.get_redis_conn(db=settings.SESSION_REDIS_DB)

    def initialize(self, init_context=True):
        self.user_service = service.user_serv
        self.context = self.__init_context(init_context)

    def __init_context(self, init_context):
        context = {}
        if init_context:
            context['now_time'] = TimeHelper.time_2_str()
        return context

    def gene_html(self, template_name_prefix, template_name_suffix='.html', layout=True):
        return tenjin_engine.render(os.path.join(os.path.dirname(__file__), template_name_prefix + template_name_suffix), self.context, layout=layout)

    def render(self, template_name_prefix, template_name_suffix='.html', layout=True):
        self.write(self.gene_html(template_name_prefix, template_name_suffix, layout))
#         self.finish()

    def raise_http_error(self, err_code, err_info=None):
        if not err_info:
            err_info = traceback.format_exc()
        if err_info:
            self.log_err(err_info)
        if 'X-Requested-With' in self.request.headers and 'XMLHttpRequest' == self.request.headers['X-Requested-With']:
            self.set_status(err_code)
            self.finish()
        else:
            self.context['err_code'] = err_code
            self.render('views/err', layout=False)

    def ajax_result(self, result):
        #self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.write(json.dumps(result, ensure_ascii=False))
#         self.finish()

    def list_parms(self, params, empty_err_code=None):
        if not params:
            if empty_err_code:
                self.raise_http_error(empty_err_code)
            return []
        return params.split('/')

    def __set_session_attr__(self, name, value):
        Session(self).__setattr__(name, value)

    def __get_session_attr__(self, name):
        return Session(self).__getattr__(name)

    def __del_session_attr__(self, name):
        Session(self).__delattr__(name)

    def __destory_session__(self):
        Session(self).__destory__()

    def log_err(self, err):
        log.access_log.error(err)

class Session(object):
    _prefix = "_session:"
    _id = None
    _skip = ['_redis', '_request', '_id']
    def __init__(self, request):
        self._redis = request._redis
        self._request = request
        # init session id
        _id = request.get_secure_cookie('sessionid')
        if _id and self._redis.exists(_id):
            self._id = _id

    def init_session(self):
        """初始化"""
        if not self._id:
            self._id = self.generate_session_id()
            self._request.set_secure_cookie('sessionid', self._id)
        self.__set_expire()

    def generate_session_id(self):
        """Generate a random id for session"""
        secret_key = self._request.settings['cookie_secret']
        ip = self._request.request.remote_ip
        while True:
            rand = os.urandom(16)
            now = time.time()
            sessionid = sha1("%s%s%s%s" % (rand, now, ip, secret_key))
            sessionid = self._prefix + sessionid.hexdigest()
            if not self._redis.exists(sessionid):
                break
        return sessionid

    def __set_expire(self):
        # 延期过期时间
        self._redis.hset(self._id, 'lastActive', time.time())
        self._redis.expire(self._id, settings.SESSION_MAXLIFETIME)

    def __getattr__(self, name):
        if self._id:
            self.__set_expire()
            return self._redis.hget(self._id, name)
        if not name in self._skip:
            return None
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if not name in self._skip:
            self.init_session()
            self._redis.hset(self._id, name, value)
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if not name in self._skip:
            return self._redis.hdel(self._id, name)
        object.__delattr__(self, name)

    def __destory__(self):
        self._redis.delete(self._id)

def auto_login(require_login=True):
    def wrapper(fn):
        def login(request, *args):
            user = request.__get_session_attr__('user')
            if not user:
                user_id = request.get_secure_cookie('user_id')
                save_me = None
#                 save_me = request.get_secure_cookie('save_me')
                if user_id and save_me:
                    user = request.user_service.find_one({'_id' : user_id})
                    if user:
                        request.__set_session_attr__('user', user)
            else:
                user = eval(user)
            if user:
                request.current_user = user
                request.context['curr_user'] = user
            else:
                if require_login:
                    if 'X-Requested-With' in request.request.headers and 'XMLHttpRequest' == request.request.headers['X-Requested-With']:
                        request.set_status(403)
                        request.finish()
                    else:
                        request.redirect("/auth/login")
                    return None
            return fn(request, *args)
        return login
    return wrapper

def logout():
    def wrapper(fn):
        def _do(request, *args):
            request.__destory_session__()
            request.set_secure_cookie('save_me', '', 0)
            request.set_secure_cookie('user_id', '', 0)
            return fn(request, *args)
        return _do
    return wrapper

def except_err():
    def wrapper(fn):
        def _except(request, *args):
            try:
                return fn(request, *args)
            except:
                request.raise_http_error(request.SERVER_ERROR, traceback.format_exc())
            finally:
                pass
        return _except
    return wrapper


class ErrHandler(BaseHandler):

    def get(self, res):
        if res:
            try:
                fns = os.path.dirname(__file__).split(os.sep)[:-1]
                fns.append(res)
                if os.path.exists(os.sep.join(fns)):
                    rf = open(os.sep.join(fns))
                    self.finish(rf.read())
                else:
                    self.write('go fuck yourself!')
            except:
                self.raise_http_error(self.URL_NOT_FOUND)
            finally:
                return
        self.raise_http_error(self.URL_NOT_FOUND)

    def post(self, res):
        self.get()
