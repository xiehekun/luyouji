#coding:utf-8
'''
Created on 2014-6-27

@author: 596572
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

import exception
from scrapy.selector import Selector
from scrapy.http.request import Request
from utils import item_generators, _md5, decorators, build_req_meta
import settings
import re
from scrapy.http.request.form import FormRequest
from scrapy.spider import Spider

class QY(Spider):
    '''
    http://place.qyer.com/
    '''
    name = 'qyer'

    def __init__(self, **kwargs):
        c_url = kwargs.pop('c_url', None) # if get start with a single country url
        self.c_single = True
        if c_url:
            self.start_urls = [c_url]
        else:
            self.c_single = False
            self.start_urls = [
                               'http://place.qyer.com/'
                               ]

    def get_countries_in_continent(self, hxs, node_id):
        '''
        According to the node_id in html source code, get all countries for every continent.
        '''
        continent_node = hxs.xpath('//div[@id="%s"]' % node_id)
        continent_name_node = continent_node.xpath('h2[position() = 1]/em/a/child::text()')
        continent_names = continent_name_node.extract()[0]
        continent_zh_name = continent_names.split(' ')[0].strip()
        continent_en_name = ' '.join(continent_names.split(' ')[1:]).strip()

        country_nodes = continent_node.xpath('div//li[@class="item"]//a')
        for cn in country_nodes:
            country_url = cn.xpath('@href').extract()[0]
            country_zh_name = cn.xpath('child::text()').extract()[0].strip()
            country_en_name = cn.xpath('span/child::text()').extract()[0].strip()
            yield continent_zh_name, continent_en_name, country_url, country_zh_name, country_en_name

    @decorators.handle_err_and_sleep(sleep=False)
    def parse(self, resp):
        '''
        parse http://place.qyer.com/, get all continents and countries.
        or
        parse a single country.
        '''
        hxs = Selector(resp)
        if self.c_single:
            continent_url = hxs.xpath('//div[@class="qyer_head_crumbg"]/div[@class="qyer_head_crumb"]//span[@class="text drop"][position() = 2]/a/@href').extract()[0].strip()
            continent_en_name = re.search('^http://place.qyer.com/([a-z]+)/$', string=continent_url).group(1).strip()
            continent_en_name = continent_en_name[0].upper() + continent_en_name[1:]
            continent_zh_name = hxs.xpath('//div[@class="qyer_head_crumbg"]/div[@class="qyer_head_crumb"]//span[@class="text drop"][position() = 2]/a/text()').extract()[0].strip()

            country_zh_name = hxs.xpath('//p[@class="pl_topbox_cn fontYaHei"]/a/text()').extract()[0].strip()
            country_en_name = hxs.xpath('//p[@id="pl_topbox_en"]/a/text()').extract()[0].strip()
            item = item_generators.gene_country(continent_zh_name, continent_en_name, country_zh_name, country_en_name)
            c_id = str(item['_id'])
            yield item
            yield Request(url=resp._get_url(), meta={'c_id' : c_id}, callback=self.parse_country)
        else:
            node_ids = ['Asialist', 'Europelist', 'Africalist', 'NorthAmericalist', 'SouthAmericalist', 'Oceanialist', 'Antarcticalist']
            for node_id in node_ids:
                countries = self.get_countries_in_continent(hxs, node_id)
                if not countries:
                    continue
                for country in countries:
                    item = item_generators.gene_country(country[0], country[1], country[3], country[4])
                    c_id = str(item['_id'])
                    yield item
                    yield Request(url=country[2], meta={'c_id' : c_id}, callback=self.parse_country)

    def get_region(self, nodes, cls):
        '''
        get all regions for country.
        '''
        if cls == 'line':
            for n in nodes:
                zh_name = n.xpath('child::text()').extract()
                if zh_name:
                    zh_name = zh_name[0].strip()
                else:
                    zh_name = ''
                en_name = n.xpath('span[@class="en"]/child::text()').extract()
                if en_name:
                    en_name = en_name[0].strip()
                else:
                    en_name = ''
                url = n.xpath('@href').extract()[0]
                yield zh_name, en_name, url
        else:
            for n in nodes:
                name = n.xpath('child::text()').extract()[0]
                ns = name.split(' ')
                if re.findall(ur'[\u4e00-\u9fa5]', ns[0]):
                    zh_name = ns[0]
                    if len(ns) > 1:
                        en_name = ' '.join(ns[1:]).strip()
                    else:
                        en_name = ''
                else:
                    zh_name = ''
                    en_name = name.strip()
                url = n.xpath('@href').extract()[0]
                yield zh_name, en_name, url

    @decorators.handle_err_and_sleep(sleep=False)
    def parse_country(self, resp):
        '''
        parse the country page, and get all regions for current country.
        contain two type of region: city and area(include park and other area(i.e the state fo U.S.A)).
        then yield requests to parse the sight, food, shopping information for every region.
        '''
        hxs = Selector(resp)
        c_id = resp.meta['c_id']
        clses = {'line' : settings.region_city_type, 'arealist' : settings.region_area_type}
        for cls in clses:
            nodes = hxs.xpath('//div[@id="allcitylist"]/div[@class="%s"]//li//a' % cls)
            regions = self.get_region(nodes, cls)
            if regions:
                _type = clses[cls]
                for region in regions:
                    item = item_generators.gene_region_no_guide(region[0], region[1], _type, c_id)
                    r_id = item['_id']
                    yield item
                    url = region[2]

                    for point in settings.qyer_region_crawl_points:
                        r_url = (url + point) if url.endswith('/') else (url + '/' + point)
                        point_type = point
                        yield Request(url=r_url, meta=build_req_meta(resp, {'r_id' : r_id, 'point_type' : point_type}), callback=self.parse_region_points)

    @decorators.handle_err_and_sleep(sleep=False)
    def parse_region_points(self, resp):
        '''
        parse sight, food, shopping points.
        '''
        page = 1 if not 'page' in resp.meta else resp.meta['page']
        point_nodes = []
        next_nodes = None
        append_meta = {}
        if page == 1: # if true, means current page is sync http request, so can get some useful information two next pages.
            hxs = Selector(resp)
            read_more_url = hxs.xpath('//p[@class="readMore"]/a/@href').extract()
            if read_more_url:
                yield Request(read_more_url[0], meta=build_req_meta(resp), callback=self.parse_region_guide)

            point_nodes = hxs.xpath('//div[@id="poilistdiv"]//li/h3[@class="title"]/a')
            next_nodes = hxs.xpath('//div[@id="poilistdiv"]//a[@data-bn-ipg="pages-5"]')
            content = resp._get_body()
            m = re.search("var categoryid = '([0-9]+)';", content)
            append_meta['point_cateid'] = m.group(1)
            m = re.search("var belong_id = '([0-9]+)';", content)
            append_meta['point_id'] = m.group(1)
        else: # if true, means current page is async http request
            data = eval('u' + '"""' + resp._get_body().strip() + '"""').replace('\\', '').\
                    replace('\r', '').replace('\n', '').replace('\t', '').replace("'", '"').\
                    replace('</div>"}}', "</div>'}}").replace('</li></ul>"}}', "</li></ul>'}}").replace('"data":{"html":"', """"data":{"html":'""")

            data = eval(data.strip())
            hxs = Selector(text=data['data']['html'])
            point_nodes = hxs.xpath('//li/h3[@class="title"]/a')
            next_nodes = hxs.xpath('//a[@data-bn-ipg="pages-5"]')
#         point_type = resp.meta['point_type']
#         for point_node in point_nodes:
#             url = point_node.xpath('@href').extract()[0]
#             callback = None
#             if hasattr(self, 'parse_' + point_type):
#                 callback = eval('self.parse_' + point_type)
#             if callback:
#                 yield Request(url=url, meta=resp.meta, callback=callback)
        for point_node in point_nodes:
            url = point_node.xpath('@href').extract()[0]
            yield Request(url=url, meta=build_req_meta(resp, append_meta), callback=self.parse_point)

        if next_nodes:
            url = 'http://place.qyer.com/ajax.php'
            append_meta['page'] = page + 1
            new_req_meta = build_req_meta(resp, append_meta)
            _req_body = {'type' : 'city', 'order' : '0', 'action' : 'ajaxpoi', 'page' : str(page + 1), 'pagesize' : '16'}
            _req_body['id'] = str(new_req_meta['point_id'])
            _req_body['cateid'] = str(new_req_meta['point_cateid'])
            yield FormRequest(url, callback=self.parse_region_points, formdata=_req_body, meta=new_req_meta)

    @decorators.handle_err_and_sleep(sleep=False)
    def parse_region_guide(self, resp):
        hxs = Selector(resp)
        guide = hxs.xpath('//div[@class="pla_main2"]//div[@class="pla_txtquote"]/p//child::text()').extract()
        if guide:
            yield item_generators.gene_region_guide(resp.meta['r_id'], ''.join(guide), resp.meta['point_type'])

    @decorators.handle_err_and_sleep(sleep=False)
    def parse_point(self, resp):
        r_id = resp.meta['r_id'] # region id
        _type = resp.meta['point_type']

        append_meta = {}
        hxs = Selector(resp)
        names = hxs.xpath('//a[@data-bn-ipg="place-poi-top-title"]/child::text()').extract()
        if len(names) == 1:
            name = names[0]
            if re.findall(ur'[\u4e00-\u9fa5]', name):
                zh_name = name
                en_name = ''
            else:
                en_name = name
                zh_name = ''
        else:
            en_name = names[0]
            zh_name = names[1]

        point_id = _md5(r_id + (en_name if en_name else zh_name) + _type)
        append_meta['point_id'] = point_id
        pic_url = hxs.xpath('//a[@data-bn-ipg="place-poidetail-cover"]/@href').extract()
        if pic_url:
            yield Request(url=pic_url[0], meta=build_req_meta(resp, append_meta), callback=self.parse_point_pics)
        coordinate = None
        map_src = hxs.xpath('//div[@class="pla_sidemap"]//img/@src').extract()
        if map_src: # 41.889019,12.480851
            m = re.search('icon_mapno_big.png\|([0-9.,-]+)\&sensor=false', map_src[0])
            if m:
                coordinate = m.group(1)

        desc = None
        desc_nodes = hxs.xpath('//div[@id="summary_box"]')
        if desc_nodes:
#             desc = ''.join(desc_nodes[0].xpath('.//child::text()').extract()).strip()
            desc = [txt.strip() for txt in desc_nodes[0].xpath('.//child::text()').extract()]

        details = {}
        detail_nodes = hxs.xpath('//ul[@class="pla_textdetail_list"]/li')
        for detail_node in detail_nodes:
            k = detail_node.xpath('./span[@class="tit"]/text()').extract()[0].replace(u'：', '')
            txt_node = detail_node.xpath('./p[@class="txt"] | ./div[@class="txt poiDetailMarkdown"]')
            tags = txt_node.xpath('./a//text()').extract()
            if tags:
                v = tags
            else:
                v = [txt.strip() for txt in txt_node.xpath('./p//text()').extract()]

            nv = []
            for vv in v:
                if not vv or not vv.strip():
                    continue
                nv.append(vv)

            details[k] = nv

        yield item_generators.gene_point(point_id, resp.meta['c_id'], r_id, en_name, zh_name, coordinate, desc, details, _type)


        comments = hxs.xpath('//div[@id="poicommentlist"]/div[@class="pl_yelp"]//p[@class="text"]/child::text()').extract()
        comments = [c[c.index('：') + 1:] if not c.find('：') == -1 else c for c in comments]
        if comments:
            yield item_generators.gene_point_comments(point_id, comments, _type)

        if not details:
            raise exception.NoNodeParsed('no details nodes been parsed.')

    @decorators.handle_err_and_sleep(sleep=False)
    def parse_point_pics(self, resp):
        hxs = Selector(resp)
        img_urls = hxs.xpath('//a[@class="_jsbigphotoinfo"]/img/@src').extract()
        if img_urls and len(img_urls) > settings.img_download_limit:
            img_urls = img_urls[:settings.img_download_limit]
        r_img_urls = []
        for img_url in img_urls:
            i = img_url.rindex('/')
            img_url = img_url[:i] + '/980x576'
            r_img_urls.append(img_url)
        yield item_generators.gene_point_imgs(resp.meta['point_id'], r_img_urls)

    def __str__(self):
        return self.name
