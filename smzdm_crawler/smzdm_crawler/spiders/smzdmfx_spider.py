# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from scrapy.spiders import Spider

from smzdm_crawler.items import SmzdmCrawlerItem


class SmzdmfxSpider(Spider):
    name = "smzdm"
    allowed_domains = "smzdm.com"
    start_urls = ["http://faxian.smzdm.com/"]
    
    def parse(self, response):
        print "parse"
        
        selector = BeautifulSoup(response.body)
        lists = selector.findAll("li", {"class":"list"})
        
        for list in lists:
            item = SmzdmCrawlerItem()
            item['name'] = list.find("h2", {"class":"itemName"}).find("span", {"class":"black"}).get_text() 
            item['id'] = list.attrs['articleid']
            yield item