#coding:utf-8
# import md5
import base64
import json
from email.mime.text import MIMEText
import smtplib
import traceback
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

def _json(o, dumps=True, ensure_ascii=False, indent=None, encoding='utf-8'):
    if dumps:
        return json.dumps(obj=o, ensure_ascii=ensure_ascii, indent=indent, encoding=encoding)
    else:
        return json.loads(s=o, encoding=encoding)

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
        return False
