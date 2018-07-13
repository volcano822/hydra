# -*- coding: utf-8 -*-

import datetime
import socket

import scrapy
from hydra.items import DoubanBookItem
from scrapy.http import Request


class DoubanBookSpider(scrapy.Spider):
    name = 'douban_book'

    host = 'https://book.douban.com'

    def start_requests(self):
        return [
            Request('https://book.douban.com/tag/?view=cloud',
                    callback=self.parse_tag_list)]

    def parse_tag_list(self, response):
        '''
        解析登录页隐藏参数，并发起验证码请求
        :param response:
        :return:
        '''
        tag_cols = response.xpath('//table[@class="tagCol"]')
        for index, tag_col in enumerate(tag_cols):
            hrefs = tag_col.xpath('./tbody/tr/td/a/@href').extract()
            for href in hrefs:
                page_nums = 20
                # 前5页数据
                for i in range(5):
                    yield Request(self.host + href + ("?start=%d&type=T" % (i * page_nums)),
                                  callback=self.parse_tag_detail)

    def parse_tag_detail(self, response):
        '''
        解析产品信息，并
        :param response:
        :return:
        '''
        tag = response.xpath('//*[@id="content"]/h1/text()').extract_first()
        tag = tag.replace(u'豆瓣图书标签: ', '')
        book_infos = response.xpath('//li[@class="subject-item"]/div[@class="info"]')
        for index, book_info in enumerate(book_infos):
            item = DoubanBookItem()
            name = book_info.xpath('./h2/a/text()').extract_first()
            name = name.strip()
            item['name'] = name
            item['tag'] = tag
            pub_info = book_info.xpath('./div[@class="pub"]/text()').extract_first()
            item['publish_info'] = pub_info.strip()
            rating_score = book_info.xpath(
                    './div[@class="star clearfix"]/span[@class="rating_nums"]/text()').extract_first()
            item['rating_score'] = rating_score.strip()
            rating_persons = book_info.xpath('./div[@class="star clearfix"]/span[@class="pl"]/text()').extract_first()
            item['rating_persons'] = rating_persons.strip()
            abstract = book_info.xpath('./p/text()').extract_first()
            item['abstract'] = abstract.strip()

            item["url"] = response.url
            item["project"] = self.settings.get('BOT_NAME')
            item["spider"] = self.name
            item["spider"] = socket.gethostname()
            item["date"] = datetime.datetime.now()

            yield item
