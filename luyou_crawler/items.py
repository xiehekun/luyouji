#coding:utf-8
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class Country(Item):
    _id = Field()
    continent_en_name = Field()
    continent_zh_name = Field()

    en_name = Field()
    zh_name = Field()

    def _get_values(self):
        return self._values

class RegionNoGuide(Item):
    _id = Field()
    en_name = Field()
    zh_name = Field()
    _type = Field()
    country_id = Field()

    def _get_values(self):
        return self._values

class RegionWithGuide(Item):
    _id = Field()
    _type = Field()
    guide = Field()

    def _get_values(self):
        return {'_id' : self['_id'], self['_type'] + '_guide' : self['guide']}


class Point(Item):
    _id = Field()
    _type = Field()
    en_name = Field()
    zh_name = Field()
    coordinate = Field()
    desc = Field()
    details = Field()
    country_id = Field()
    region_id = Field()

    def _get_values(self):
        tmp_values = self._values
        tmp_values.pop('_type')
        return tmp_values

class PointComments(Item):
    _id = Field()
    _type = Field()
    comments = Field()

    def _get_values(self):
        tmp_values = self._values
        tmp_values.pop('_type')
        return tmp_values

class PointImgs(Item):
    _id = Field()
    images = Field()
    image_urls = Field()

    def _get_values(self):
        tmp_values = self._values
        tmp_values.pop('image_urls')
        images = tmp_values['images']
        r_images = []
        if images:
            for img in images:
                r_images.append(img['path'])
        tmp_values['images'] = r_images
        return tmp_values
















class Sight(Item):
    _id = Field()
    en_name = Field()
    zh_name = Field()
    coordinate = Field()
    desc = Field()
    details = Field()

class SightComment(Item):
    _id = Field()
    comments = Field()

class SightImgs(Item):
    _id = Field()
    images = Field()
    image_urls = Field()
