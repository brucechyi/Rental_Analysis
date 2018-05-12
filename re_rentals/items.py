# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ReRentalsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    price = scrapy.Field()
    bedroom = scrapy.Field()
    bathroom = scrapy.Field()
    zipcode = scrapy.Field()
    address = scrapy.Field()