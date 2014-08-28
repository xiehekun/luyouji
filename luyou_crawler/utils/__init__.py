# coding:utf-8
# import md5
import base64
import json
from email.mime.text import MIMEText
import smtplib
import traceback
import cookielib
import urllib2
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

def send_mail(to_list, sub, content):
    # 设置服务器，用户名、口令以及邮箱的后缀
    mail_host = "smtp.sina.com"
    mail_user = "luyouji2014"
    mail_pass = "luyouji"
    mail_postfix = "sina.com"
    me = mail_user + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEText(content, _subtype='html', _charset='utf8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = to_list
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user + "@" + mail_postfix, mail_pass)
        s.sendmail(me, to_list, msg.as_string())
        s.close()
        return True
    except:
        return False

def init_opener(host=None):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.79 Safari/535.11'), \
                         ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'), \
                         ('Accept-Charset', 'GBK,utf-8;q=0.7,*;q=0.3'), \
                         ('Accept-Encoding', 'gzip,deflate,sdch'), \
                         ('Accept-Language', 'zh-CN,zh;q=0.8'), \
                         ('Connection', 'keep-alive')
                         ]
    if host:
        opener.addheaders.append(('Host', host))
    urllib2.install_opener(opener);

def load_data(url, data=None, decode=True, return_url=False, encoding="utf-8"):
    init_opener()
    opener = urllib2.build_opener()
    page = opener.open(fullurl=url, data=data)
    return_data = page.read()
    url = page.url
    if decode:
        return_data = return_data.decode(encoding, 'ignore')
    if return_url:
        return (return_data, url)
    return return_data

def build_req_meta(resp, append={}):
    n_meta = {}
    for k in resp.meta:
        n_meta[k] = resp.meta[k]
    for k in append:
        n_meta[k] = append[k]
    return n_meta

