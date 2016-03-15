# -*- coding: utf-8 -*-
import random

from bs4 import BeautifulSoup
from scrapy.spiders import Spider

from spider_wxhui.utils.load_content import loadJsonContent
from spider_wxhui.utils.load_content import load_content
import urllib


class gzh_newrank_spider(Spider):
    name = "gzh_new"
    
    
    def __init__(self):
        self.allowed_domains = "baidu.com"
        self.start_urls = ["http://www.baidu.com/"]
        self.zixun = ["时事", "民生", "财富", "科技", "创业", "汽车", "楼市", "职场", "教育", "学术", "政务", "企业"]
        self.life = ["文化", "百科", "健康", "时尚", "美食", "乐活", "旅行", "幽默", "情感", "体娱", "美体", "文摘"]
    
    def parse(self, response):
        print "parse"
        
        self.parse_category()
        
        
    def parse_category(self):
        print "parse_category"
        
        url = "http://newrank.cn/xdnphb/list/day/rank"
        #params
        rank_name = random.choice(self.zixun) 
        rank_name_group = "资讯"
        data = {"end":"2016-03-14", "rank_name":rank_name, "rank_name_group":rank_name_group, "nonce":"a8b88d251", "xyz":"295864d70c0d4cc7b50cbc0f47d7991d", "start":"2016-03-14"}
        params = urllib.urlencode(data)
        print params
        selector = loadJsonContent(url, method='POST', host='www.newrank.cn', origin="http://newrank.cn", cookie= "CNZZDATA1253878005=1121863735-1458026465-null%7C1458026465", refer="http://newrank.cn/public/info/list.html?type=data&period=day", Accept="application/json", params=params)
        if selector is None: return
        print selector
        
#         category_zixuns = selector.find("div", {"class":"zixun"}).findAll("li")
#         for item in category_zixuns:
#             print item.find("a").attrs['data']
        
        
        
        