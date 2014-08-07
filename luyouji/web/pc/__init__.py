#coding: utf-8
from collections import OrderedDict
from utils import common, settings
from web import BaseHandler, auto_login, except_err, logout
import datetime
import entity
import re
import time
import service
import tornado
import json
import StringIO


###################index handler##################
class IndexHandler(BaseHandler):

    def initialize(self):
        BaseHandler.initialize(self)

    @auto_login()
    def get(self):
        self.render('views/index')

    def post(self):
        self.get()

###################login handler###################
class AuthHandler(BaseHandler):

    CODE_NAME_PWD_EMPTY = 0 # user_name or pass_word is None or empty.
    CODE_USER_NOT_EXISTS = 2 # user is not exists.
    CODE_LOGIN_SUCC = 3 # login succeeded.
    CODE_LOGIN_PWD_ERR = 4 # user_name or pass_word is error.
    CODE_REGIST_USER_NAME_ERROR = 5 # regist user name is not a email address.
    CODE_REGIST_PASSWD_EMPTY = 6 # regist password is empty.
    CODE_REGIST_PASSWD_NOT_SAME = 7 # regist two password is not same.
    CODE_REGIST_USER_EXISTS = 8 # regist the user is already exists.
    CODE_REGIST_USER_SUCCED = 9 # regist succeeded.
    CODE_THIRD_LOGIN_AUTH_FAILED = 10

    def initialize(self):
        BaseHandler.initialize(self)
        self.email_reg = '^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$'

    def get(self, m, *args):
        m = '_' + m
        if not hasattr(self, m) or m in self._skip_attrs:
            self.raise_http_error(self.URL_NOT_FOUND)
        else:
            eval("self." + m + "()")

    def post(self, m, *args): # m in ('login', 'regist', 'uppwd')
        if not hasattr(self, m) or m in self._skip_attrs:
            self.raise_http_error(self.URL_NOT_FOUND)
        else:
            eval("self." + m + "()")

#     @logout()
    def _logout(self):
        user_id = self.get_secure_cookie('user_id')
        self.__destory_session__()
        self.set_secure_cookie('save_me', '', 0)
        self.set_secure_cookie('user_id', '', 0)
        source = self.get_secure_cookie('source')
        if not source and user_id:
            source = self.user_service.find_one({'_id' : user_id})['source']
        if source and int(source) > 0: # third
            self.context['source'] = source
            self.context['source_key'] = self.get_secure_cookie('source_key')
            self.context['source_token'] = self.get_secure_cookie('source_token')
            self.set_secure_cookie('source', '', 0)
            self.set_secure_cookie('source_key', '', 0)
            self.set_secure_cookie('source_token', '', 0)
            self.render('views/logout', layout=False)
        else:
            self.redirect('/auth/login')

    @auto_login(require_login=False)
    def _login(self):
        if self.current_user:
            self.redirect('/')
        else:
            self.render('views/login')

    @except_err()
    def login(self):
        user_name = self.get_argument('user_name', None)
        pass_word = self.get_argument('pass_word', None, False)
#         save_me = self.get_argument('saveme', 0)

        succ = True
        code = None
        user = None
        if not user_name or not pass_word:
            succ = False
            code = self.CODE_NAME_PWD_EMPTY
        if succ:
            user = self.user_service.find_one({'user_name' : user_name})
            if not user:
                succ = False
                code = self.CODE_USER_NOT_EXISTS
            else:
                if not common._md5(pass_word) == user['pass_word']:
                    succ = False
                    code = self.CODE_LOGIN_PWD_ERR
        if not succ:
            return self.ajax_result({'succ' : succ, 'code' : code})

        self.__set_session_attr__('user', user)
        self.set_secure_cookie('user_id', user['_id'], 365 * 10)
        self.set_secure_cookie('source', str(0), 365 * 10)
#         self.set_secure_cookie('save_me', '1', int(save_me))
        self.ajax_result({'succ' : True})

    @except_err()
    def thirdlogin(self):
        _type = self.get_argument('type', None)
        open_id = self.get_argument('openId', None)
        access_token = self.get_argument('accessToken', '')
        nickname = self.get_argument('nickname', None)
        figureurl = self.get_argument('figureurl', None)
        succ = True
        code = -1
        if not _type or not open_id:
            succ = False
            code = self.CODE_THIRD_LOGIN_AUTH_FAILED
        source = 0 #本站
        if _type == 'qq':
            source = 1 #qq
        if _type == 'weibo':
            source = 2 #weibo
        if succ:
            _id = common._md5(_type + open_id)
            u = self.user_service.find_one({'source' : source, 'open_id' : open_id})
            if not u:
                self.user_service.insert({'_id' : _id, 'source' : source, 'source_key' : open_id, 'source_token' : access_token, 'nickname' : nickname, 'figureurl' : figureurl, 'regist_time' : time.time()})
            else:
                self.user_service.update({'source' : source, 'open_id' : open_id}, {'source_token' : access_token, 'nickname' : nickname, 'figureurl' : figureurl})
            u = self.user_service.find_one({'_id' : _id})
            self.__set_session_attr__('user', u)
            self.set_secure_cookie('user_id', u['_id'], 365 * 10)
            self.set_secure_cookie('source', str(source), 365 * 10)
            self.set_secure_cookie('source_key', str(open_id), 365 * 10)
            self.set_secure_cookie('source_token', str(access_token), 365 * 10)
            self.ajax_result({'succ' : True})
        else:
            self.ajax_result({'succ' : False, 'code' : code})


    @logout()
    def _regist(self):
        self.render('views/regist')

    @except_err()
    def regist(self):
        user_name = self.get_argument('user_name', '')
        pass_word = self.get_argument('pass_word', None, False)
        c_pass_word = self.get_argument('c_pass_word', None, False)
        succ = True
        code = None
        if not re.match(self.email_reg, user_name, re.IGNORECASE):
            succ = False
            code = self.CODE_REGIST_USER_NAME_ERROR
        if succ and (not pass_word or not c_pass_word):
            succ = False
            code = self.CODE_REGIST_PASSWD_EMPTY
        if succ and not pass_word == c_pass_word:
            succ = False
            code = self.CODE_REGIST_PASSWD_NOT_SAME
        if succ and self.user_service.find_one({'user_name' : user_name}):
            succ = False
            code = self.CODE_REGIST_USER_EXISTS
        if not succ:
            return self.ajax_result({'succ' : succ, 'code' : code})

        now_timestamp = time.time()
        _id = common._md5(s=user_name + str(now_timestamp))
        self.user_service.insert({
                                            '_id' : _id,
                                            'user_name' : user_name,
                                            'pass_word'  : common._md5(pass_word),
                                            'regist_time' : now_timestamp,
                                            'source' : settings.default_user_source,
                                            'source_key' : settings.default_user_source_key
                                        })
        user = self.user_service.find_one({'_id' : _id})
        self.__set_session_attr__('user', user)
        self.set_secure_cookie('user_id', user['_id'], 365 * 10)
        self.ajax_result({'succ' : True, 'code' : self.CODE_REGIST_USER_SUCCED})

    def findpwd(self):
        user_name = self.get_argument('user_name', '')
        succ = True
        if not re.match(self.email_reg, user_name, re.IGNORECASE):
            succ = False
            code = self.CODE_REGIST_USER_NAME_ERROR
        if succ:
            u = self.user_service.find_one({'user_name' : user_name})
            if not u:
                succ = False
                code = self.CODE_USER_NOT_EXISTS
        if not succ:
            return self.ajax_result({'succ' : False, 'code' : code})
        reset_code = common._md5(user_name + str(time.time()))
        self._redis.setex(settings.reset_code_redis_prefix + reset_code, user_name, 24 * 60 * 60)
        reset_url = settings.server_domain + '/auth/resetpwd?code=%s' % reset_code
        self.context['reset_url'] = reset_url
        mail_content = self.gene_html('views/findpwd', layout=False)
        succ = common.send_mail(user_name, '路游记        找回密码', mail_content)
        self.ajax_result({'succ' : succ})

    def _resetpwd(self):
        reset_code = self.get_argument('code', '')
        if not reset_code:
            return self.raise_http_error(self.URL_NOT_FOUND)
        user_name = self._redis.get(settings.reset_code_redis_prefix + reset_code)
        self.context['expire'] = False
        if not user_name:
            self.context['expire'] = True
        self.context['user_name'] = user_name if user_name else ''
        self.render('views/resetpwd')

    def resetpwd(self):
        user_name = self.get_argument('user_name', '')
        pass_word = self.get_argument('pass_word', None, False)
        c_pass_word = self.get_argument('c_pass_word', None, False)
        succ = True
        code = None
        if not re.match(self.email_reg, user_name, re.IGNORECASE):
            succ = False
            code = self.CODE_REGIST_USER_NAME_ERROR
        if succ and (not pass_word or not c_pass_word):
            succ = False
            code = self.CODE_REGIST_PASSWD_EMPTY
        if succ and not pass_word == c_pass_word:
            succ = False
            code = self.CODE_REGIST_PASSWD_NOT_SAME
        if not succ:
            return self.ajax_result({'succ' : succ, 'code' : code})
        n_pwd = common._md5(pass_word)
        self.user_service.update({'user_name' : user_name}, {'$set' : {'pass_word' : n_pwd}})
        self.ajax_result({'succ' : True})

############################ plan handler #########################
class PlanHandler(BaseHandler):

    PLAN_NAME_EMPTY = 0
    PLAN_DATE_EMPTY = 1
    PLAN_DATE_END_SMALLER = 2

    PLAN_DAY_DEST_EMPTY = 3
    PLAN_DAY_IDS_EMPTY = 4
    PLAN_DAY_TYPE_EMPTY = 5
    PLAN_DAY_DAY_EMPTY = 6

    PLAN_DAY_POINT_ID_NONE = 7

    PLAN_NOT_FOUND = 8

    def initialize(self):
        BaseHandler.initialize(self)
        self.plan_service = service.plan_serv
        self.plan_detail_service = service.plan_detail_serv
        self.country_service = service.country_serv
        self.region_service = service.region_serv
        self.region_point_service = service.region_point_serv
        self.plan_page_size = 5

    @except_err()
    @auto_login()
    def get(self, m, params=None):
        m = '_' + m
        if not hasattr(self, m) or m in self._skip_attrs:
            self.raise_http_error(self.URL_NOT_FOUND)
        else:
            eval("self." + m + "(params)")

    @except_err()
    @auto_login()
    def post(self, m, params=None):
        if params and params.strip():
            m = m + '_' + params.strip()
        if not hasattr(self, m) or m in self._skip_attrs:
            self.raise_http_error(self.URL_NOT_FOUND)
        else:
            eval("self." + m + "()")

    def _page(self, params):
        params = self.list_parms(params)
        page = 1
        if params:
            page = int(params[0])
        plan_page = self.plan_service.find_page(page, self.plan_page_size, {'user_id' : self.current_user['_id']}, [('create_time', -1), ('end_date', -1)])
        self.ajax_result(plan_page)

    def new(self):
        plan_name = self.get_argument('plan_name', None)
        start_date = self.get_argument('start_date', None)
        end_date = self.get_argument('end_date', None)
        succ = True
        code = None
        if not plan_name:
            succ = False
            code = self.PLAN_NAME_EMPTY
        if succ and (not start_date or not end_date):
            succ = False
            code = self.PLAN_DATE_EMPTY
        if succ and (end_date < start_date):
            succ = False
            code = self.PLAN_DATE_END_SMALLER
        if not succ:
            return self.ajax_result({'succ' : succ, 'code' : code})

        user_id = self.current_user['_id']
        now_timestamp = time.time()
        _id = common._md5(user_id + str(now_timestamp) + plan_name)
        doc = {'_id': _id,'user_id' : user_id,
               'name' : plan_name, 'start_date' : start_date, 'end_date' : end_date, 'create_time' : now_timestamp}
        details = []
        details_days = {}
        days = (datetime.datetime.strptime(end_date, '%Y-%m-%d') - datetime.datetime.strptime(start_date, '%Y-%m-%d')).days + 1
        for i in xrange(1, days + 1):
            pd_id = common._md5(_id + str(i))
            details.append(pd_id)
            details_days[pd_id] = common.TimeHelper.time_2_str(t=datetime.datetime.strptime(start_date, '%Y-%m-%d'), frt='%Y-%m-%d', delta=(i - 1), delta_unit="days")
        doc['details'] = details
        doc['days'] = days
        self.plan_service.insert(doc)
        self.ajax_result({'succ' : True})
        self.plan_detail_service.init_details(_id, details_days)

    def _del(self, params):
        params = self.list_parms(params, empty_err_code=self.URL_NOT_FOUND)
        if not params:
            return
        _id = params[0]
        self.plan_service.remove({'_id' : _id})
        self.ajax_result({'succ' : True})
        self.plan_detail_service.remove({'p_id' : _id})

    def _index(self, params):
        params = self.list_parms(params, empty_err_code=self.URL_NOT_FOUND)
        if not params:
            return
        _id = params[0]
        plan = self.plan_service.find_one({'_id' : _id})
        if not plan:
            return self.raise_http_error(self.URL_NOT_FOUND, 'plan id %s is not exists.' % _id)

        details = plan['details']
#         first_pd_id = None
        if details:
#             first_pd_id = details[0]
            self.context['day_details'] = self.plan_detail_service.find({'_id' : {'$in' : details}}, sort=[('day', 1)])
#         if first_pd_id:
#             first_pd = self.plan_detail_service.find_one({'_id' : first_pd_id})
#             self.context['first_plan_detail'] = first_pd
#         self.context['countries'] = json.dumps(obj=self.country_service.find_all(), ensure_ascii=False)
        self.context['plan'] = plan
        self.render('views/plan', layout=False)

    def day(self):
        dest_region_id = self.get_argument('dest_region_id', None)
        dest_region_name = self.get_argument('dest_region_name', None)
        p_id = self.get_argument('p_id', None)
        _id = self.get_argument('_id', None)
        _type = self.get_argument('type', None)
        day = self.get_argument('day', None)
        succ = True
        code = None
        if not p_id or not _id:
            succ = False
            code = self.PLAN_DAY_IDS_EMPTY
        if succ and (not dest_region_name and not dest_region_id):
            succ = False
            code = self.PLAN_DAY_DEST_EMPTY
        if succ and not _type:
            succ = False
            code = self.PLAN_DAY_TYPE_EMPTY
        if succ and not day:
            succ = False
            code = self.PLAN_DAY_DAY_EMPTY
        if not succ:
            return self.ajax_result({'succ' : succ, 'code' : code})

        if not dest_region_id:
            dest_region_id = ""
        plan_detail = self.plan_detail_service.find_one({'_id' : _id})
        dd_id = common._md5(p_id + _id + _type + dest_region_id + str(time.time()))
        day_details = []
        day_detail = {'_type' : _type, 'dest_region_id' : dest_region_id, 'dest_region_name' : dest_region_name,
                      'dest_input_type' : (settings.plan_day_detail_dest_type_sys if dest_region_id else settings.plan_day_detail_dest_type_cus),
                      'dd_id' : dd_id,
                      'imgs' : [], 'points' : [], 'txts' : [], 'enable' : True}
        day_details.append(day_detail)
        if not plan_detail:
            doc = {'_id' : _id, 'p_id' : p_id, 'day' : day}
            doc['day_details'] = day_details
            self.plan_detail_service.insert(doc)
        else:
            self.plan_detail_service.update({'_id' : _id}, {'$push' : {'day_details' : day_detail}})
        pds = self.plan_detail_service.find_one({'_id' : _id})
        for pd in pds['day_details']:
            if pd['dd_id'] == dd_id:
                self.ajax_result({'succ' : True, 'data' : {'plan_detail' : pd}})
                break

    def _day(self, params):
        params = self.list_parms(params, empty_err_code=self.URL_NOT_FOUND)
        if not params:
            return
        _id = params[0].split('_')[0]
        pd_id = params[0].split('_')[1]
        p = self.plan_service.find_one({'_id' : _id})
        if not p:
            return self.ajax_result({'succ' : False, 'code' : self.PLAN_NOT_FOUND})
        end_date = common.TimeHelper.time_2_str(t=datetime.datetime.strptime(p['end_date'], '%Y-%m-%d'), frt='%Y-%m-%d', delta=-1, delta_unit="days")
        self.plan_service.update({'_id' : _id}, {'$pull' : {'details' : pd_id}, '$set' : {'end_date' : end_date}})
        self.plan_detail_service.remove({'_id' : pd_id})
        self.ajax_result({'succ' : True})

    def _day_add(self, params):
        params = self.list_parms(params, empty_err_code=self.URL_NOT_FOUND)
        if not params:
            return
        _id = params[0]
        plan = self.plan_service.find_one({'_id' : _id})
        if not plan:
            return self.ajax_result({'succ' : False, 'code' : self.PLAN_NOT_FOUND})
        pds = self.plan_detail_service.find({'_id' : {'$in' : plan['details']}}, sort=[('day', 1)])
        n_pd_id = common._md5(_id + str(time.time()))
        if not pds:
            n_day = common.TimeHelper.time_2_str(frt='%Y-%m-%d')
        else:
            n_day = common.TimeHelper.time_2_str(t=datetime.datetime.strptime(pds[-1]['day'], '%Y-%m-%d'), frt='%Y-%m-%d', delta=1, delta_unit="days")
        self.plan_service.update({'_id' : _id}, {'$addToSet' : {'details' : n_pd_id}, '$set' : {'end_date' : n_day}})
        self.plan_detail_service.insert({'_id' : n_pd_id, 'p_id' : _id, 'day' : n_day})
        pd = self.plan_detail_service.find_one({'_id' : n_pd_id})
        self.ajax_result(pd)

    def day_details(self):
        _id = self.get_argument('_id', None)
        dd_id = self.get_argument('dd_id', None)
        if not _id or not dd_id:
            return self.ajax_result({'succ' : False, 'code' : self.PLAN_DAY_IDS_EMPTY})
        txt = self.get_argument('txt', None)
        imgs = self.get_argument('imgs', None)
        points = self.get_argument('points', None)
        conditions = {'_id' : _id, 'day_details.dd_id' : dd_id}
        push_doc = {}
        txts = []
        if not txt is None:
#             push_doc['day_details.0.txts'] = txt
            txts.append(txt)
#         if imgs:
#             push_doc['day_details.$.imgs'] = imgs.split(',')
#         if points:
#             push_doc['day_details.$.points'] = points.split(',')
#         if not push_doc:
#             self.ajax_result({'succ' : True})
#         else:
#             self.plan_detail_service.update(conditions, update_doc={'$addToSet' : push_doc, '$set' : {'txts' : txts}})
        self.plan_detail_service.update(conditions, update_doc={'$set' : {'day_details.$.txts' : txts}})

        self.ajax_result({'succ' : True})

    def _day_detail(self, params):
        params = self.list_parms(params, empty_err_code=self.URL_NOT_FOUND)
        if not params:
            return
        pd_id = params[0]
        dd_id = self.get_argument('dd_id', None)
        if not dd_id:
            return self.ajax_result({'succ' : True})
        self.plan_detail_service.update({'_id' : pd_id, 'day_details.dd_id' : dd_id}, {'$set' : {'day_details.$.enable' : False}})
        return self.ajax_result({'succ' : True})

    def day_point(self, params=None):
        point_id = self.get_argument('point_id', None)
        succ = True
        code = None
        if not point_id:
            succ = False
            code = self.PLAN_DAY_POINT_ID_NONE
        if not succ:
            return self.ajax_result({'succ' : False, 'code' : code})
        _id = self.get_argument('_id')
        dd_id = self.get_argument('dd_id')
        self.plan_detail_service.update({'_id' : _id, 'day_details.dd_id' : dd_id}, {'$addToSet' : {'day_details.$.points' : point_id}})
        _type = self.get_argument('point_type', '')
        self.ajax_result({'succ' : True, 'data' : {'point' : self.region_point_service.find_one(_type, conditions={'_id' : point_id})}})

    def _day_point(self, params=None):
        point_id = self.get_argument('point_id', None)
        succ = True
        code = None
        if not point_id:
            succ = False
            code = self.PLAN_DAY_POINT_ID_NONE
        if not succ:
            return self.ajax_result({'succ' : False, 'code' : code})
        _id = self.get_argument('_id')
        dd_id = self.get_argument('dd_id')
        self.plan_detail_service.update({'_id' : _id, 'day_details.dd_id' : dd_id}, {'$pull' : {'day_details.$.points' : point_id}})
        self.ajax_result({'succ' : True})

    def _day_img(self, params=None):
        _id = self.get_argument('_id')
        dd_id = self.get_argument('dd_id')
        img_url = self.get_argument('img_url', '')
        if not img_url:
            return self.ajax_result({'succ' : True})
        self.plan_detail_service.update({'_id' : _id, 'day_details.dd_id' : dd_id}, {'$pull' : {'day_details.$.imgs' : img_url}})
        self.ajax_result({'succ' : True})

    def _day_imgs(self, params=None):
        _id = self.get_argument('_id')
        dd_id = self.get_argument('dd_id')
        pd = self.plan_detail_service.find_one({'_id' : _id, 'day_details.dd_id' : dd_id}, {"day_details.$" : 1})
        self.ajax_result(pd['day_details'][0]['imgs'])

########################## common handler ###############################
import qiniu.conf
qiniu.conf.ACCESS_KEY = settings.qiqiu_access_key
qiniu.conf.SECRET_KEY = settings.qiqiu_secret_key
import qiniu.rs
policy = qiniu.rs.PutPolicy(settings.qiqiu_bucket_name)
uptoken = policy.token()
import qiniu.io

class CommonHandler(BaseHandler):

    def initialize(self):
        BaseHandler.initialize(self)
        self.country_service = service.country_serv
        self.region_service = service.region_serv
        self.region_point_service = service.region_point_serv
        self.plan_detail_service = service.plan_detail_serv
        self.imgs_service = service.imgs_serv

    @except_err()
    def get(self, m, params=None):
        m = '_' + m
        if not hasattr(self, m) or m in self._skip_attrs:
            self.raise_http_error(self.URL_NOT_FOUND)
        else:
            eval("self." + m + "(params)")

    @except_err()
    def post(self, m, params=None):
        if not hasattr(self, m) or m in self._skip_attrs:
            self.raise_http_error(self.URL_NOT_FOUND)
        else:
            eval("self." + m + "(params)")

    def _sea_city(self, params=None):
        q = self.get_argument('q', '')
        l = self.get_argument('limit', '20')
        res = self.region_service.find({'$or' : [{'zh_name' : {'$regex' : '.*' + q + '.*', '$options' : 'i'}}, {'en_name' : {'$regex' : '.*' + q + '.*', '$options' : 'i'}}]}, sort=[('en_name', 1)], limit=int(l))
#         self.ajax_result(res)
        s = ""
        if not res:
            s = "None"
        else:
            for r in res:
                s = s + json.dumps(r, ensure_ascii=False) + "\n"
        self.finish(s.strip())

    def _countries(self, params=None):
        self.ajax_result(self.country_service.find())

    def _sea_regions(self, params=None):
        _ids = self.get_argument("_ids", None)
        if not _ids:
            return self.ajax_result([]);
        self.ajax_result(self.region_service.find({'_id' : {'$in' : _ids.split(',')}}))

    def _sea_points(self, params=None):
        q = self.get_argument('q', '')
        l = self.get_argument('limit', '20')
        t = self.get_argument('point_type', None);
        region_id = self.get_argument('region_id', None)
        if not t:
            return self.raise_http_error(self.URL_NOT_FOUND)
        res = []
        if region_id:
            res = self.region_point_service.find(t, {'region_id' : region_id, '$or' : [{'zh_name' : {'$regex' : '.*' + q + '.*', '$options' : 'i'}}, {'en_name' : {'$regex' : '.*' + q + '.*', '$options' : 'i'}}]}, sort=[('en_name', 1)], limit=int(l))
        else:
            res = self.region_point_service.find(t, {'$or' : [{'zh_name' : {'$regex' : '.*' + q + '.*', '$options' : 'i'}}, {'en_name' : {'$regex' : '.*' + q + '.*', '$options' : 'i'}}]}, sort=[('en_name', 1)], limit=int(l))
        if res is None:
            return self.raise_http_error(self.URL_NOT_FOUND)
        s = ""
        if not res:
            s = "None"
        else:
            for r in res:
                s = s + json.dumps(r, ensure_ascii=False) + "\n"
        self.finish(s.strip())

    def _point(self, params):
        params = self.list_parms(params, empty_err_code=self.URL_NOT_FOUND)
        if not params:
            return
        type_id = params[0]
        _type = type_id.split('_')[0]
        _id = type_id.split('_')[1]
        point = self.region_point_service.find_one(_type, {'_id' : _id})
        if not point:
            return self.raise_http_error(self.URL_NOT_FOUND)
        self.context['point'] = point
        self.context['_type'] = _type
        self.context['img_prefix'] = settings.point_img_prefix
        imgs = self.imgs_service.find_one({'_id' : _id})
        if imgs:
            self.context['imgs'] = imgs['images']
        self.render('views/point')

    def _region(self, params):
        params = self.list_parms(params, empty_err_code=self.URL_NOT_FOUND)
        if not params:
            return
        _id = params[0]
        self.context['region'] = self.region_service.find_one({'_id' : _id})
        self.render('views/region', layout=False)

    def _points(self, params=None):
        sight_ids = self.get_argument(settings.region_point_sight, None)
        food_ids = self.get_argument(settings.region_point_food, None)
        shopping_ids = self.get_argument(settings.region_point_shopping, None)
        sights = []
        if sight_ids:
            sights = self.region_point_service.find(settings.region_point_sight, {'_id' : {'$in' : sight_ids.split(',')}})
        foods = []
        if food_ids:
            foods = self.region_point_service.find(settings.region_point_food, {'_id' : {'$in' : food_ids.split(',')}})
        shoppings = []
        if shopping_ids:
            shoppings = self.region_point_service.find(settings.region_point_shopping, {'_id' : {'$in' : shopping_ids.split(',')}})

        self.ajax_result({
                          settings.region_point_sight : sights,
                          settings.region_point_food : foods,
                          settings.region_point_shopping : shoppings
                         })

    @auto_login()
    def _upload(self, params):
        params = self.list_parms(params, empty_err_code=self.URL_NOT_FOUND)
        if not params:
            return
        id_ddid = params[0]
        _id = id_ddid.split('_')[0]
        dd_id = id_ddid.split('_')[1]
        self.context['_id'] = _id
        self.context['dd_id'] = dd_id
        self.render('views/upload', layout=False)

    FILE_UPLOAD_LACK_PARAM = 1
    FILE_UPLOAD_NONE_FILE = 2
    FILE_UPLOAD_NOTALLOWED_EXT = 3
    FILE_UPLOAD_IMAGE_TOO_BIG = 4
    FILE_UPLOAD_FAILED = 5

    IMAGE_TYPE_LIST = ['image/gif', 'image/jpeg',
                       'image/pjpeg', 'image/bmp', 'image/png', 'image/x-png']
    MAX_IMAGE_SIZE = 4 * 1024 * 1024

    @auto_login()
    def upload(self, params):
        params = self.list_parms(params)
        if not params:
            return self.ajax_result({'succ' : False, "code" : self.FILE_UPLOAD_LACK_PARAM})
        id_ddid = params[0]
        _id = id_ddid.split('_')[0]
        dd_id = id_ddid.split('_')[1]
        files = self.request.files
        if not files:
            return self.ajax_result({'succ' : False, "code" : self.FILE_UPLOAD_NONE_FILE})
        f = files['files'][0]
        if not f['content_type'] in self.IMAGE_TYPE_LIST:
            return self.ajax_result({'succ' : False, "code" : self.FILE_UPLOAD_NOTALLOWED_EXT})
        if len(f['body']) > self.MAX_IMAGE_SIZE:
            return self.ajax_result({'succ' : False, 'code' : self.FILE_UPLOAD_IMAGE_TOO_BIG})

        extra = qiniu.io.PutExtra()
        extra.mime_type = f['content_type']
        data = StringIO.StringIO(f['body'])
        ret, err = qiniu.io.put(uptoken, common._md5(f['body'] + str(time.time())), data, extra)
        if err is not None:
            return self.ajax_result({'succ' : False, 'code' : self.FILE_UPLOAD_FAILED, "msg" : str(err)})
        img_url = settings.qiqiu_img_url_prefix + ret['key']
        self.ajax_result({'succ' : True, 'img_url' : img_url, '_id' : _id, 'dd_id' : dd_id})

        self.plan_detail_service.update({'_id' : _id, 'day_details.dd_id' : dd_id}, {'$addToSet' : {'day_details.$.imgs' : img_url}})

    def _map(self, params):
        params = self.list_parms(params)
        if not params:
            return self.ajax_result({'succ' : False, "code" : self.FILE_UPLOAD_LACK_PARAM})
        x = params[0].split(',')[0]
        y = params[0].split(',')[1]
        self.context['x'] = x
        self.context['y'] = y

        self.render('views/map', layout=False)

    def _tlogin(self, params=None):
        self.render('views/tlogin')
