#coding:utf-8
# encoding: utf-8
# Created on 2014-6-30
# @author: binge
from utils import _md5
from items import Country, Sight, SightComment, SightImgs,\
    RegionNoGuide, RegionWithGuide, Point, PointComments, PointImgs

def gene_country(continent_zh, continent_en, country_zh, country_en):
    item = Country()
    item['_id'] = _md5(continent_en + country_en)
    item['continent_en_name'] = continent_en
    item['continent_zh_name'] = continent_zh
    item['zh_name'] = country_zh
    item['en_name'] = country_en
    return item

def gene_region_no_guide(region_zh, region_en, _type, country_id, gene_mth='en'):
    item = RegionNoGuide()
    if gene_mth == 'en':
        item['_id'] = _md5(country_id + region_en)
    else:
        item['_id'] = _md5(country_id + region_zh)
    item['zh_name'] = region_zh
    item['en_name'] = region_en
    item['_type'] = _type
    item['country_id'] = country_id
    return item

def gene_region_guide(_id, guide, _type):
    item = RegionWithGuide()
    item['_id'] = _id
    item['guide'] = guide
    item['_type'] = _type
    return item

def gene_point(_id, country_id, region_id, en_name, zh_name, coordinate, desc, details, _type):
    item = Point()
    item['_id'] = _id
    item['_type'] = _type
    item['country_id'] = country_id
    item['region_id'] = region_id
    item['en_name'] = en_name
    item['zh_name'] = zh_name
    item['coordinate'] = coordinate
    item['desc'] = desc
    item['details'] = details
    return item

def gene_point_comments(_id, comments, _type):
    item = PointComments()
    item['_id'] = _id
    item['_type'] = _type
    item['comments'] = comments
    return item

def gene_point_imgs(_id, img_urls):
    item = PointImgs()
    item['_id'] = _id
    item['image_urls'] = img_urls
    return item













########################################################################################
def gene_sight(_id, country_id, region_id, en_name, zh_name, coordinate, desc, details):
    item = Sight()
    item['_id'] = _id
    item['country_id'] = country_id
    item['region_id'] = region_id
    item['en_name'] = en_name
    item['zh_name'] = zh_name
    item['coordinate'] = coordinate
    item['desc'] = desc
    item['details'] = details
    return item

def gene_sight_comment(_id, comments):
    item = SightComment()
    item['_id'] = _id
    item['comments'] = comments
    return item

def gene_sight_imgs(_id, img_urls):
    item = SightImgs()
    item['_id'] = _id
    item['image_urls'] = img_urls
    return item
