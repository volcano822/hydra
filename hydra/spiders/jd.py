# -*- coding: utf-8 -*-

import base64
import datetime
import json
import logging
import random
import socket

from hydra.items import JdOrderItem

import re
import scrapy
from PIL import Image
from scrapy.http import Request, FormRequest


class JdSpider(scrapy.Spider):
    name = 'jd'
    login_data = {}
    login_url = ""

    def start_requests(self):
        return [
            Request('https://passport.jd.com/new/login.aspx',
                    callback=self.parse_welcome)]

    def get_entrypt_pwd(self, pwd, pub_key):
        '''
        获取加密后的密码，rsa加密目前不可用
        '''
        from Crypto.Cipher import PKCS1_v1_5
        from Crypto.PublicKey import RSA
        pubkey = """-----BEGIN PUBLIC KEY-----
        {}
        -----END PUBLIC KEY-----"""

        rsakey = RSA.importKey(pubkey.format(pub_key))
        cipher = PKCS1_v1_5.new(rsakey)
        entrypt_pwd = base64.b64encode(cipher.encrypt(pwd))
        return entrypt_pwd

    def parse_welcome(self, response):
        '''
        解析登录页隐藏参数，并发起验证码请求
        :param response:
        :return:
        '''
        loginname = raw_input("手机号>>>")
        print loginname
        password = raw_input("密码>>>")
        print password
        uuid = response.xpath('//input[@id="uuid"]/@value').extract_first()
        if not uuid:
            uuid = ""
        self.login_url = "https://passport.jd.com/uc/loginService?uuid=%s&ltype=logout&r=%f&version=2015" % (
            uuid, random.random())
        eid = response.xpath('//input[@id="eid"]/@value').extract_first()
        if not eid:
            eid = ""
        fp = response.xpath('//input[@id="sessionId"]/@value').extract_first()
        if not fp:
            fp = ""
        _t = response.xpath('//input[@id="token"]/@value').extract_first()
        if not _t:
            _t = ""
        loginType = response.xpath('//input[@id="loginType"]/@value').extract_first()
        if not loginType:
            loginType = ""
        authcode_img = "https:" + response.xpath('//img[@id="JD_Verification1"]/@src2').extract_first()
        pubKey = response.xpath('//input[@id="pubKey"]/@value').extract_first()
        if not pubKey:
            pubKey = ""
        sa_token = response.xpath('//input[@id="sa_token"]/@value').extract_first()
        if not sa_token:
            sa_token = ""

        data = {
            "uuid": uuid,
            "eid": eid,
            "fp": fp,
            "_t": _t,
            "loginType": loginType,
            "loginname": loginname,
            "nloginpwd": self.get_entrypt_pwd(password, pubKey),
            "authcode": "",
            "pubKey": pubKey,
            "sa_token": sa_token
        }
        self.login_data = data
        return Request(authcode_img, callback=self.parse_capcha)

    def parse_capcha(self, response):
        '''
        解析验证码，发起登录
        :param response:
        :return:
        '''
        # 获取验证码，将验证马写入本地
        with open('capcha.jpg', 'wb') as f:
            f.write(response.body)
        try:
            # 利用pillow打开验证码
            im = Image.open('capcha.jpg')
            im.show()
        except:
            print('请打开文件%s自行输入' % ("capcha.jpg"))
        cap = raw_input("请输入验证码>>")
        self.login_data['authcode'] = cap
        print self.login_data
        return FormRequest(self.login_url, formdata=self.login_data, callback=self.parse_login)

    def parse_login(self, response):
        '''
        解析登录信息；登录成功，跳到订单列表页
        :param response:
        :return:
        '''
        if response.text.find('success') != -1:
            self.log("login success", logging.INFO)
        else:
            self.log(response.text, logging.ERROR)
            raise Exception("login failed")

        url = "https://order.jd.com/center/list.action"
        return Request(url, callback=self.parse_order_list)

    def parse_order_list(self, response):
        '''
        解析订单列表，并请求订单产品信息
        :param response:
        :return:
        '''
        data = re.findall(u"ORDER_CONFIG\['orderWareIds'\]='(.+?)';\r\n", response.text)
        if len(data) > 0:
            orderWareIds = data[0]
        data = re.findall(u"ORDER_CONFIG\['orderWareTypes'\]='(.+?)';\r\n", response.text)
        if len(data) > 0:
            orderWareTypes = data[0]
        data = re.findall(u"ORDER_CONFIG\['orderIds'\]='(.+?)';\r\n", response.text)
        if len(data) > 0:
            orderIds = data[0]
        data = re.findall(u"ORDER_CONFIG\['orderTypes'\]='(.+?)';\r\n", response.text)
        if len(data) > 0:
            orderTypes = data[0]
        data = re.findall(u"ORDER_CONFIG\['orderSiteIds'\]='(.+?)';\r\n", response.text)
        if len(data) > 0:
            orderSiteIds = data[0]

        params = {
            "orderWareIds": orderWareIds,
            "orderWareTypes": orderWareTypes,
            "orderIds": orderIds,
            "orderTypes": orderTypes,
            "orderSiteIds": orderSiteIds,
        }
        return FormRequest("https://order.jd.com/lazy/getOrderProductInfo.action", formdata=params,
                           callback=self.parse_product_info)

    def parse_product_info(self, response):
        '''
        解析产品信息，并
        :param response:
        :return:
        '''
        data = json.loads(response.text)
        for it in data:
            item = JdOrderItem()
            item['name'] = it['name']
            item['product_id'] = it['productId']
            item['category_string'] = it['categoryString']

            item["url"] = response.url
            item["project"] = self.settings.get('BOT_NAME')
            item["spider"] = self.name
            item["spider"] = socket.gethostname()
            item["date"] = datetime.datetime.now()
            yield item
