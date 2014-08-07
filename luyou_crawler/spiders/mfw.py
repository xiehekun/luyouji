# coding:utf-8
# Created on 2014-8-1
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from scrapy.spider import Spider
import exception
import settings
from scrapy.http.request import Request
from utils import item_generators, cfgs, decorators
import re
from scrapy.selector import Selector
import utils

crawl_min_secs = 8
crawl_max_secs = 15

class MFW(Spider):

    name = 'mfw'

    def __init__(self, **kwargs):
        self.domain = 'http://www.mafengwo.cn'
        self.start_urls = [self.domain]
        self.province_regions_url_pattern = 'http://www.mafengwo.cn/gonglve/sg_ajax.php?sAct=getMapData&iMddid=%s&iType=3&iPage=1'
        self.region_url_pattern = 'http://www.mafengwo.cn/travel-scenic-spot/mafengwo/%s.html'
        self.point_url_pattern = 'http://www.mafengwo.cn/%s/%s/gonglve.html'
#         self.point_pics_url_pattern = 'http://www.mafengwo.cn/photo/poi/%s.html'
        self.point_pics_url_pattern = 'http://www.mafengwo.cn/mdd/ajax_photolist.php?act=getPoiPhotoList&mddid=%s&poiid=%s&page=1'
        self.big_pic_size = '.w665_500.'
        self.small_pic_size = '.w235.'
        self.anti_crawler_warning = False
        self.anti_crawler_kw = u'验证码'

    @decorators.handle_err_and_sleep(min_secs=crawl_min_secs, max_secs=crawl_max_secs)
    def parse(self, resp):
        item = item_generators.gene_country('亚洲', 'Asia', '中国', 'China')
        c_id = str(item['_id'])
        yield item
        for zh_name in settings.mfw_satrt_urls_info:
            info = settings.mfw_satrt_urls_info[zh_name]
            _type = info['type']
            url = info['url']
            mfw_id = re.search('^http://www.mafengwo.cn/travel-scenic-spot/mafengwo/([0-9]+).html$', url).group(1)
            if _type == 0:
                url = self.province_regions_url_pattern % mfw_id
                yield Request(url, meta={'c_id' : c_id}, callback=self.parse_province)
            if _type == 1:
                en_name = cfgs.chinese_region_en_name(zh_name)
                if en_name:
                    gene_mth = 'en'
                else:
                    gene_mth = 'zh'
                item = item_generators.gene_region_no_guide(zh_name, en_name, settings.region_city_type, c_id, gene_mth)
                region_id = str(item['_id'])
                yield item

                resp.meta['mfw_region_id'] = mfw_id
                resp.meta['region_id'] = region_id
                resp.meta['c_id'] = c_id
                for p in settings.mfw_region_crawl_points:
                    resp.meta['point_type'] = p
                    yield Request(self.point_url_pattern % (p, mfw_id), meta=resp.meta, callback=self.parse_region_points)
        yield None

    @decorators.handle_err_and_sleep(min_secs=crawl_min_secs, max_secs=crawl_max_secs)
    def parse_province(self, resp):
        regions = utils._json(o=resp._get_body(), dumps=False)['list']
        for region in regions:
            mfw_region_id = region['id']
            zh_name = region['name']
            c_id = resp.meta['c_id']
            en_name = cfgs.chinese_region_en_name(zh_name)
            if en_name:
                gene_mth = 'en'
            else:
                gene_mth = 'zh'
            item = item_generators.gene_region_no_guide(zh_name, en_name, settings.region_city_type, c_id, gene_mth)
            region_id = item['_id']
            yield item

            resp.meta['mfw_region_id'] = mfw_region_id
            resp.meta['region_id'] = region_id
            for p in settings.mfw_region_crawl_points:
                resp.meta['point_type'] = p
                yield Request(self.point_url_pattern % (p, mfw_region_id), meta=resp.meta, callback=self.parse_region_points)

    @decorators.handle_err_and_sleep(min_secs=crawl_min_secs, max_secs=crawl_max_secs)
    def parse_region_points(self, resp):
        hxs = Selector(resp)
        point_nodes = hxs.xpath('//div[@class="m-recList"]//ul[@class="poi-list"]//div[@class="title"]//a')
        if not point_nodes:
            raise exception.NoNodeParsed('no point nodes been parsed.')

        for point_node in point_nodes:
            point_url = self.domain + point_node.xpath('@href').extract()[0]
            point_name = point_node.xpath('text()').extract()[0]
            resp.meta['point_name'] = point_name
            yield Request(point_url, meta=resp.meta, callback=self.parse_point)

        next_page_url = hxs.xpath('//a[@class="ti next"]/@href').extract()
        if next_page_url:
            yield Request(self.domain + next_page_url[0], meta=resp.meta, callback=self.parse_region_points)

    @decorators.handle_err_and_sleep(min_secs=crawl_min_secs, max_secs=crawl_max_secs)
    def parse_point(self, resp):
        region_id = resp.meta['region_id']
        mfw_region_id = resp.meta['mfw_region_id']
        pics_url = self.point_pics_url_pattern % (mfw_region_id, re.search('http://www.mafengwo.cn/poi/([0-9]+).html', resp._get_url()).group(1))

        country_id = resp.meta['c_id']
        zh_name = resp.meta['point_name']
        _type = cfgs.mfw_point_db_name(resp.meta['point_type'])
        point_id = utils._md5(region_id + (zh_name) + _type)
        resp.meta['point_id'] = point_id

        yield Request(url=pics_url, callback=self.parse_point_pics, meta=resp.meta)

        content = resp._get_body()
        m = re.search("lat: parseFloat\('([0-9.]+)'\)", content)
        if not m:
            coordinate = ""
        else:
            lat = m.group(1)
            lng = re.search("lng: parseFloat\('([0-9.]+)'\)", content).group(1)
            coordinate = '%s,%s' %(lat, lng)

        hxs = Selector(resp)

        detail_title_nodes = hxs.xpath("//div[@id='comment_header']//div[@class='bd']/h3")
        detail_content_nodes = hxs.xpath("//div[@id='comment_header']//div[@class='bd']/p")
        desc = ''
        details = {}
        for i in xrange(0, len(detail_title_nodes)):
            k = detail_title_nodes[i].xpath('./text()').extract()[0].strip()
            if k == u'简介':
                desc = detail_content_nodes[i].xpath('./text()').extract()
            else:
                if k == u'相关预订':
                    continue
                details[k] = [txt.strip() for txt in detail_content_nodes[i].xpath('.//child::text()').extract()]

        yield item_generators.gene_point(point_id, country_id, region_id, '', zh_name, coordinate, desc, details, _type)

        comments = hxs.xpath('//div[@class="comment-item"]//div[@class="c-content"]/p/text()').extract()
        if comments:
            yield item_generators.gene_point_comments(point_id, comments, _type)

        if not details and not desc:
            raise exception.NoNodeParsed('no details nodes been parsed.')

    @decorators.handle_err_and_sleep(min_secs=crawl_min_secs, max_secs=crawl_max_secs)
    def parse_point_pics(self, resp):
        hxs = Selector(resp)
        img_urls = hxs.xpath('//img/@src').extract()
        if img_urls and len(img_urls) > settings.img_download_limit:
            img_urls = img_urls[:settings.img_download_limit]
        r_img_urls = []
        for img_url in img_urls:
            r_img_urls.append(img_url.replace(self.small_pic_size, self.big_pic_size))
        yield item_generators.gene_point_imgs(resp.meta['point_id'], r_img_urls)



    def __str__(self, **kwargs):
        return self.name


