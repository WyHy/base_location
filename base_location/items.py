# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaseLocationItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    errcode = scrapy.Field()
    lac = scrapy.Field()
    cid = scrapy.Field()
    lat = scrapy.Field()
    lon = scrapy.Field()
    address = scrapy.Field()
