# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class PropertiesItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    # Primary fields
    house_url = Field()
    village = Field()
    village_url = Field()
    house_info = Field()
    flood_info = Field()
    area = Field()
    area_url = Field()
    subway = Field()
    taxfree = Field()
    total_price = Field()
    total_price_unit = Field()
    unit_price = Field()

    # Housekeeping fields
    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()


class JdOrderItem(Item):
    # Primary fields
    name = Field()
    product_id = Field()
    category_string = Field()

    # Housekeeping fields
    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()


class DoubanBookItem(Item):
    # Primary fields
    name = Field()
    tag = Field()
    publish_info = Field()
    rating_score = Field()
    rating_persons = Field()
    abstract = Field()

    # Housekeeping fields
    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()
