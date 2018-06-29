# -*- coding: utf-8 -*-
import datetime
import json
import logging
import socket
import urlparse

from properties.items import PropertiesItem

import scrapy
from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join


class LjSpider(scrapy.Spider):
    '''
    抓取链家在售二手房资源（北京）
    '''
    name = 'lj'
    allowed_domains = ['bj.lianjia.com']
    start_urls = ['https://bj.lianjia.com/ershoufang/']

    def parse(self, response):
        self.log(response.url, level=logging.INFO)

        # 处理分页
        page_url = response.xpath('//div[@class="page-box house-lst-page-box"]/@page-url').extract_first()
        if not page_url:
            self.parse_item(response)
            return
        page_data = response.xpath('//div[@class="page-box house-lst-page-box"]/@page-data').extract_first()
        page_data = json.loads(page_data)
        page_num = page_data['totalPage']
        i = 1
        while (i <= page_num):
            yield Request(urlparse.urljoin("https://bj.lianjia.com", page_url.replace('{page}', str(i)))
                          , callback=self.parse_item)
            i = i + 1

    def parse_item(self, response):
        """ 该方法解析一个房源列表页

        @url https://bj.lianjia.com/ershoufang/
        @returns items 20
        @scrapes house_url village village_url house_info  flood_info area area_url subway taxfree total_price total_price_unit unit_price
        @scrapes url project spider server date
        """
        lis = response.xpath('//li[@class="clear"]')
        for index, li in enumerate(lis):
            l = ItemLoader(item=PropertiesItem(), selector=li)
            l.add_xpath('house_url', './a[@class="img "]/@href', MapCompose(unicode.strip), Join(separator="\t"))
            l.add_xpath('village', './div/div[@class="address"]/div[@class="houseInfo"]/a/text()',
                        MapCompose(unicode.strip), Join(separator="\t"))
            l.add_xpath('village_url', './div/div[@class="address"]/div[@class="houseInfo"]/a/@href',
                        MapCompose(unicode.strip), Join(separator="\t"))
            l.add_xpath('house_info', './div/div[@class="address"]/div[@class="houseInfo"]/text()',
                        MapCompose(unicode.strip), Join(separator="\t"))
            l.add_xpath('flood_info', './div/div[@class="flood"]/div[@class="positionInfo"]/text()',
                        MapCompose(unicode.strip), Join(separator="\t"))
            l.add_xpath('area', './div/div[@class="flood"]/div[@class="positionInfo"]/a/text()',
                        MapCompose(unicode.strip), Join(separator="\t"))
            l.add_xpath('area_url', './div/div[@class="flood"]/div[@class="positionInfo"]/a/@href',
                        MapCompose(unicode.strip), Join(separator="\t"))
            l.add_xpath('subway', './div/div[@class="followInfo"]/div[@class="tag"]/span[@class="subway"]/text()',
                        MapCompose(unicode.strip), Join(separator="\t"))
            l.add_xpath('taxfree', './div/div[@class="followInfo"]/div[@class="tag"]/span[@class="taxfree"]/text()',
                        MapCompose(unicode.strip), Join(separator="\t"))
            l.add_xpath('total_price',
                        './div/div[@class="followInfo"]/div[@class="priceInfo"]/div[@class="totalPrice"]/span/text()',
                        MapCompose(unicode.strip), Join(separator="\t"))
            l.add_xpath('total_price_unit',
                        './div/div[@class="followInfo"]/div[@class="priceInfo"]/div[@class="totalPrice"]/text()',
                        MapCompose(unicode.strip), Join(separator="\t"))
            l.add_xpath('unit_price',
                        './div/div[@class="followInfo"]/div[@class="priceInfo"]/div[@class="unitPrice"]/span/text()',
                        MapCompose(unicode.strip), Join(separator="\t"))

            l.add_value("url", response.url)
            l.add_value("project", self.settings.get('BOT_NAME'))
            l.add_value("spider", self.name)
            l.add_value("server", socket.gethostname())
            l.add_value("date", datetime.datetime.now())
            # 继续抓取同小区二手房源
            yield Request(li.xpath('./div/div[@class="flood"]/div[@class="positionInfo"]/a/@href').extract_first(),
                          callback=self.parse)
            yield l.load_item()
