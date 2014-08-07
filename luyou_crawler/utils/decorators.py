#coding:utf-8
# encoding: utf-8
# Created on 2014-7-1
# @author: binge
import time
import random
from scrapy import log
import traceback
from exception import NoNodeParsed
import settings
import utils
import threading
from scrapy.http.request import Request

def check_item(cls):
    def wrapper(fn):
        def _check(pipe, item, *args, **kwargs):
            if not item or not item.__class__ is cls:
                return item
            else:
                return fn(pipe, item, *args, **kwargs)
        return _check
    return wrapper

mutex = threading.Lock()
def handle_err_and_sleep(min_secs=1, max_secs=3, sleep=True):
    def wrapper(fn):
        def _handle(*args, **kwargs):
            crawler = args[0]
            resp = args[1]
            try:
                if 'proxy' in resp.meta:
                    sleep_time = settings.anti_crawler_sleep_time / 10
                else:
                    sleep_time = settings.anti_crawler_sleep_time
                if hasattr(crawler, 'anti_crawler_kw') and crawler.anti_crawler_kw in resp._get_body():
                    if not crawler.anti_crawler_warning and mutex.acquire(10):
                        if not crawler.anti_crawler_warning:
                            crawler.anti_crawler_warning = True
                        mutex.release()
                        utils.send_mail(settings.warning_email, 'anti luyou_crawler warning.', 'in %s.%s for url %s, got anti keyword %s in html, crawler will sleep %d seconds.' % (str(crawler), str(fn.func_name), str(resp._get_url()), crawler.anti_crawler_kw, sleep_time))
                if hasattr(crawler, 'anti_crawler_warning') and crawler.anti_crawler_warning:
                    time.sleep(sleep_time)
                    if crawler.anti_crawler_warning and mutex.acquire(10):
                        if crawler.anti_crawler_warning:
                            crawler.anti_crawler_warning = False
                        mutex.release()
                    yield Request(url=resp._get_url(), meta=resp.meta, callback=fn, dont_filter=True)
                else:
                    results = fn(*args, **kwargs)
                    if results:
                        for res in results:
                            if sleep:
                                i = random.randint(min_secs, max_secs)
                                time.sleep(i)
                                log.msg('in %s.%s sleep %ds for url: %s' % (str(crawler), str(fn.func_name), i, str(resp._get_url())), _level=log.DEBUG)
                            yield res
            except NoNodeParsed, ex:
                log.msg('no nodes been parsed, check html.', level=log.WARNING)
                if settings.mail_warning:
                    utils.send_mail(settings.warning_email, 'luyou_crawler warning.', 'in %s.%s for url %s, %s' % (str(crawler), str(fn.func_name), str(resp._get_url()), str(ex)))
            except:
                log.msg(message=traceback.format_exc() + '\n for url : ' + resp._get_url(), _level=log.ERROR)
        return _handle
    return wrapper
