#coding:utf-8
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from utils import conns_helper, decorators
import items, settings
from scrapy.exceptions import DropItem
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.http.request import Request
import hashlib
from scrapy import log
import utils

class LuyouImagesPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        ## start of deprecation warning block (can be removed in the future)
        def _warn():
            from scrapy.exceptions import ScrapyDeprecationWarning
            import warnings
            warnings.warn('ImagesPipeline.image_key(url) and file_key(url) methods are deprecated, '
                          'please use file_path(request, response=None, info=None) instead',
                          category=ScrapyDeprecationWarning, stacklevel=1)

        # check if called from image_key or file_key with url as first argument
        if not isinstance(request, Request):
            _warn()
            url = request
        else:
            url = request.url

        image_guid = hashlib.sha1(url).hexdigest()  # change to request.url after deprecation
        if response and response.meta and ('i_id' in response.meta):
            return 'full/%s/%s.jpg' % (response.meta['i_id'], image_guid)
        else:
            return 'full/%s.jpg' % (image_guid)

    def thumb_path(self, request, thumb_id, response=None, info=None):
        ## start of deprecation warning block (can be removed in the future)
        def _warn():
            from scrapy.exceptions import ScrapyDeprecationWarning
            import warnings
            warnings.warn('ImagesPipeline.thumb_key(url) method is deprecated, please use '
                          'thumb_path(request, thumb_id, response=None, info=None) instead',
                          category=ScrapyDeprecationWarning, stacklevel=1)

        # check if called from thumb_key with url as first argument
        if not isinstance(request, Request):
            _warn()
            url = request
        else:
            url = request.url

        thumb_guid = hashlib.sha1(url).hexdigest()  # change to request.url after deprecation
        if response and response.meta and ('i_id' in response.meta):
            return 'thumbs/%s/%s/%s.jpg' % (response.meta['i_id'], thumb_id, thumb_guid)
        else:
            return 'thumbs/%s/%s.jpg' % (thumb_id, thumb_guid)

    def get_media_requests(self, item, info):
        for x in item.get(self.IMAGES_URLS_FIELD, []):
            yield Request(url=x, headers={'Referer' : x}, meta={'i_id' : item['_id'], 'dont_proxy' : True})

    def item_completed(self, results, item, info):
        return ImagesPipeline.item_completed(self, results, item, info)

class CountryItemPipeline(object):

    @decorators.check_item(items.Country)
    @conns_helper.mongo_exec(mongo=conns_helper.get_mongo())
    def process_item(self, item, spider, **kwargs):
        mongo = kwargs['mongo']
        collections = mongo.luyou.country
        country = collections.find_one({'_id' : item['_id']})
        tmp_values = item._get_values()
        if country: # country exists, update
            _id = tmp_values.pop('_id')
            collections.update({'_id' : _id}, {'$set' : tmp_values})
        else:
            collections.insert(tmp_values)

class RegionNoGuidePipeline(object):

    @decorators.check_item(items.RegionNoGuide)
    @conns_helper.mongo_exec(mongo=conns_helper.get_mongo())
    def process_item(self, item, spider, **kwargs):
        mongo = kwargs['mongo']
        collections = mongo.luyou.region
        region = collections.find_one({'_id' : item['_id']})
        tmp_values = item._get_values()
        if region: # country exists, update
            _id = tmp_values.pop('_id')
            collections.update({'_id' : _id}, {'$set' : tmp_values})
        else:
            collections.insert(tmp_values)

class RegionWithGuidePipeline(object):

    @decorators.check_item(items.RegionWithGuide)
    @conns_helper.mongo_exec(mongo=conns_helper.get_mongo())
    def process_item(self, item, spider, **kwargs):
        mongo = kwargs['mongo']
        collections = mongo.luyou.region
        region = collections.find_one({'_id' : item['_id']})
        tmp_values = item._get_values()
        if region: # country exists, update
            _id = tmp_values.pop('_id')
            collections.update({'_id' : _id}, {'$set' : tmp_values})
        else:
            collections.insert(tmp_values)

class PointPipleline(object):

    @decorators.check_item(items.Point)
    @conns_helper.mongo_exec(mongo=conns_helper.get_mongo())
    def process_item(self, item, spider, **kwargs):
        mongo = kwargs['mongo']
        _type = item['_type']
        if _type in settings.qyer_region_crawl_points:
            collections = eval('mongo.luyou.region_' + _type)
        else:
            return item
        point = collections.find_one({'_id' : item['_id']})
        tmp_values = item._get_values()
        if point: # country exists, update
            _id = tmp_values.pop('_id')
            collections.update({'_id' : _id}, {'$set' : tmp_values})
        else:
            collections.insert(tmp_values)

class PointCommentsPipeline(object):

    @decorators.check_item(items.PointComments)
    @conns_helper.mongo_exec(mongo=conns_helper.get_mongo())
    def process_item(self, item, spider, **kwargs):
        mongo = kwargs['mongo']
        _type = item['_type']
        if _type in settings.qyer_region_crawl_points:
            collections = eval('mongo.luyou.region_' + _type + '_comments')
        else:
            return item

        comments = collections.find_one({'_id' : item['_id']})
        tmp_values = item._get_values()
        if comments: # country exists, update
            _id = tmp_values.pop('_id')
            collections.update({'_id' : _id}, {'$addToSet' : {'comments' : {'$each' : item['comments']}}})
        else:
            collections.insert(tmp_values)

class PointImgsPipeline(object):

    @decorators.check_item(items.PointImgs)
    @conns_helper.mongo_exec(mongo=conns_helper.get_mongo())
    def process_item(self, item, spider, **kwargs):
        if not item['images']:
            return None
        mongo = kwargs['mongo']
        collections = mongo.luyou.images
        image = collections.find_one({'_id' : item['_id']})
        if image:
            vs = item._get_values()
            _id = vs.pop('_id')
            collections.update({'_id' : _id}, {'$addToSet' : {'images' : {'$each' : vs['images']}}})
        else:
            collections.insert(item._get_values())

class PrintPipeline(object):

    def process_item(self, item, spider):
        if item:
            log.msg(message=utils._json(item._get_values(), indent=4), _level=log.ERROR)

class DropPipeline(object):
    '''
    if any item is transferred to this pipeline, drop it.
    '''

    def process_item(self, item, spider):
        if item:
            raise DropItem('this item(%s) is not instance of any Item.' % str(item))
