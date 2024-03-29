# encoding: utf-8
# Created on 2014-5-26
# @author: binge
import base64
import datetime
from email.mime.text import MIMEText
import smtplib
import traceback

# import md5
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

def _md5(s):
    return md5(s).hexdigest()

def _base64(s, e=True):
    if e:
        return base64.encodestring(s)
    else:
        return base64.decodestring(s)

class TimeHelper():

    @staticmethod
    def time_2_str(t=datetime.datetime.now(), frt='%Y-%m-%d %H:%M:%S', delta=None, delta_unit=None):
        '''
            this function parse time obj to str by frt parameter,
            parameter t is default datetime.datetime.now(),
            and parameter frt default %Y-%m-%d %H:%M:%S.
            delta_unit:
                        seconds
                        minutes
                        hours
                        days
                        ...
        '''
        if delta and delta_unit:
            delta_time_dict = {
                               'microseconds': lambda t, delta : t + datetime.timedelta(microseconds=delta),
                               'milliseconds': lambda t, delta : t + datetime.timedelta(milliseconds=delta),
                               'seconds' : lambda t, delta : t + datetime.timedelta(seconds=delta),
                               'minutes' : lambda t, delta : t + datetime.timedelta(minutes=delta),
                               'hours' : lambda t, delta : t + datetime.timedelta(hours=delta),
                               'days' : lambda t, delta : t + datetime.timedelta(days=delta),
                               'weeks' : lambda t, delta : t + datetime.timedelta(weeks=delta)
                               }
            t = delta_time_dict[delta_unit](t, delta)
        return t.strftime(frt)

    @staticmethod
    def get_week_no():
        return datetime.datetime.now().strftime('%Y%W')

    @staticmethod
    def get_month():
        return datetime.datetime.now().strftime('%Y%m')

def send_mail(to_list,sub,content):
    #设置服务器，用户名、口令以及邮箱的后缀
    mail_host="smtp.sina.com"
    mail_user="luyouji2014"
    mail_pass="luyouji"
    mail_postfix="sina.com"
    me=mail_user+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content,_subtype='html',_charset='utf8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = to_list
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user+"@"+mail_postfix,mail_pass)
        s.sendmail(me, to_list, msg.as_string())
        s.close()
        return True
    except:
        print traceback.format_exc()
        return False

