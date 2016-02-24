# -*- coding: utf-8 -*-
import datetime
import time

from bs4 import BeautifulSoup
from scrapy.http.request import Request
from scrapy.spiders import Spider

from smzdm_crawler.items import SmzdmCrawlerItem


class SmzdmfxSpider(Spider):
    name = "smzdm"
#     allowed_domains = "faxian.smzdm.com"
    start_urls = ["http://faxian.smzdm.com/"]
    
    def parse(self, response):
        print "parse"
        
        selector = BeautifulSoup(response.body)
            
        next_link = selector.find("li", {"class":"pagedown"}).find("a")
        if next_link:
            next_link = next_link.attrs['href']
            yield Request(url=next_link, callback=self.parse)
            
        lists = selector.findAll("li", {"class":"list"})
        for list in lists:
            detail_link = list.find("a", {"class":"picBox"}).attrs['href']
            yield Request(url=detail_link, callback=self.parse_detail)
            
    def parse_detail(self, response): 
        print "parse_detail" 
        selector = BeautifulSoup(response.body)     
        item = SmzdmCrawlerItem()
        item['name'] = selector.find("h1", {"class":"article_title"}).get_text().strip()
        item['id'] = response.url.split('/')[-2]
        item['buy_link'] = selector.find("div", {"class":"buy"}).find("a").attrs['href'] if selector.find("div", {"class":"buy"}) is not None else None
        item['image_link'] = selector.find("img", {"alt":True,"src":True}).attrs['src']
        item['worthy_num'] = int (selector.find("div", {"class":"score_rate"}).find("span", {"id":"rating_worthy_num"}).get_text().strip())
        item['unworthy_num'] = int (selector.find("div", {"class":"score_rate"}).find("span", {"id":"rating_unworthy_num"}).get_text().strip())
        item['fav_num'] = int (selector.find("a", {"class":"fav"}).find("em").get_text().strip())
        item['comment_num'] = int (selector.find("a", {"class":"comment"}).find("em", {"class":"commentNum"}).get_text().strip())
        item['crawl_time'] = int (time.time())
        
        publish_time = selector.find("div", {"class":"article_meta"}).find("span", {"class":None}).get_text().split(u"时间：")[-1]
        if len(publish_time) > 5:
            item['publish_time'] = publish_time
        else:
            item['publish_time'] = datetime.datetime.strftime(datetime.datetime.today().date(),"%Y-%m-%d") + " " +  publish_time
        yield item