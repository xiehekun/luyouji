# coding:utf-8
# Scrapy settings for lxjh_crawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'luyou_crawler'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

ITEM_PIPELINES = {
                'pipelines.LuyouImagesPipeline' : 500,
                'pipelines.CountryItemPipeline' : 501,
                'pipelines.RegionNoGuidePipeline' : 503,
                'pipelines.RegionWithGuidePipeline' : 504,
                'pipelines.PointPipleline' : 505,
                'pipelines.PointCommentsPipeline' : 506,
                'pipelines.PointImgsPipeline' : 507,
                'pipelines.DropPipeline' : 508,
#                 'pipelines.PrintPipeline' : 509
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'downloadmiddlewares.RotateUserAgentMiddleware':400,
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware' : None,
    'downloadmiddlewares.ProxiesMiddleware' : 750
}

IMAGES_STORE = '/root/luyou/imgs'

#IMAGES_THUMBS = {
#    '180x180': (180, 180),
#    '200x133': (200, 133),
#}
img_download_limit = 3

DOWNLOAD_TIMEOUT = 60
CONCURRENT_REQUESTS = 128
COOKIES_ENABLED = False

RETRY_TIMES = 5

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.79 Safari/535.11'
DEFAULT_REQUEST_HEADERS = {
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Accept-Charset': 'GBK,utf-8;q=0.7,*;q=0.3',
                           'Accept-Encoding': 'gzip,deflate,sdch',
                           'Accept-Language': 'zh-CN,zh;q=0.8',
                           'Connection': 'keep-alive'
                           }

LOG_ENABLED = True
LOG_FILE = '/root/luyou.log'
LOG_LEVEL = 'DEBUG'

MEMDEBUG_NOTIFY = ['zhiying8710@hotmail.com']
ROBOTSTXT_OBEY = False



##################################################
region_city_type = 1
region_area_type = 2

qyer_region_crawl_sight = 'sight'
qyer_region_crawl_food = 'food'
qyer_region_crawl_shopping = 'shopping'
qyer_region_crawl_points = [qyer_region_crawl_sight, qyer_region_crawl_food, qyer_region_crawl_shopping]

mongo_host = '127.0.0.1'
mongo_port = 27017




mfw_satrt_urls_info = {\
                        '新疆' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/13061.html', \
                            'type' : 0\
                        }, \
                        '西藏' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/12700.html', \
                            'type' : 0\
                        }, \
                        '甘肃' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/13295.html', \
                            'type' : 0\
                        }, \
                        '青海' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/12788.html', \
                            'type' : 0\
                        }, \
                        '内蒙古' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/12720.html', \
                            'type' : 0\
                        }, \
                        '宁夏' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/12931.html', \
                            'type' : 0\
                        }, \
                        '四川' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/12703.html', \
                            'type' : 0\
                        }, \
                        '云南' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/12711.html', \
                            'type' : 0\
                        }, \
                        '陕西' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/13083.html', \
                            'type' : 0\
                        }, \
                        '湖北' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/14731.html', \
                            'type' : 0\
                        }, \
                        '重庆' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/10208.html', \
                            'type' : 1\
                        }, \
                        '贵州' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/14103.html', \
                            'type' : 0\
                        }, \
                        '湖南' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/13732.html', \
                            'type' : 0\
                        }, \
                        '广西' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/12810.html', \
                            'type' : 0\
                        }, \
                        '海南' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/12938.html', \
                            'type' : 0\
                        }, \
                        '山西' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/13033.html', \
                            'type' : 0\
                        }, \
                        '河南' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/12967.html', \
                            'type' : 0\
                        }, \
                        '江西' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/15508.html', \
                            'type' : 0\
                        }, \
                        '广东' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/14674.html', \
                            'type' : 0\
                        }, \
                        '河北' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/14407.html', \
                            'type' : 0\
                        }, \
                        '北京' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/10065.html', \
                            'type' : 1\
                        }, \
                        '天津' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/10320.html', \
                            'type' : 1\
                        }, \
                        '山东' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/12976.html', \
                            'type' : 0\
                        }, \
                        '江苏' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/14387.html', \
                            'type' : 0\
                        }, \
                        '安徽' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/12719.html', \
                            'type' : 0\
                        }, \
                        '浙江' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/14575.html', \
                            'type' : 0\
                        }, \
                        '上海' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/10099.html', \
                            'type' : 1\
                        }, \
                        '福建' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/12871.html', \
                            'type' : 0\
                        }, \
                        '澳门' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/10206.html', \
                            'type' : 1\
                        }, \
                        '香港' : {
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/10189.html', \
                            'type' : 1\
                        }, \
                        '台湾' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/12684.html', \
                            'type' : 0\
                        }, \
                        '黑龙江' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/16712.html', \
                            'type' : 0\
                        }, \
                        '吉林' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/14871.html', \
                            'type' : 0\
                        }, \
                        '辽宁' : {\
                            'url' : 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/15148.html', \
                            'type' : 0\
                        }\
                      }

mfw_region_crawl_jd = 'jd'
mfw_region_crawl_cy = 'cy'
mfw_region_crawl_gw = 'gw'
mfw_region_crawl_points = [mfw_region_crawl_jd, mfw_region_crawl_cy, mfw_region_crawl_gw]

mail_warning = True
warning_email = '286116936@qq.com'

anti_crawler_sleep_time = 3 * 60 * 60

dont_proxy = False