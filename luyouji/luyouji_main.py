# encoding: utf-8
# Created on 2014-5-23
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from web import pc, ErrHandler
import os
from utils.common import _base64
import tornado

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret" : _base64('www.luyouji.com'),
    "gzip" : True,
}

application = tornado.web.Application([
    (r"/auth/([a-zA-Z0-9_]*)", pc.AuthHandler),
    (r"/plan/([a-zA-Z0-9_]+)/?([a-zA-Z0-9_,.]*)", pc.PlanHandler),
    (r"/common/([a-zA-Z0-9_]+)/?([a-zA-Z0-9_,.]*)", pc.CommonHandler),
    (r"/", pc.IndexHandler),
    (r"/(.+)", ErrHandler)
], **settings)


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
