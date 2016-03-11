# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class SmzdmCrawlerItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = Field()
    id = Field()
    publish_time = Field()
    crawl_time = Field()
    buy_link = Field()
    image_link = Field()
    worthy_num = Field()
    unworthy_num = Field()
    fav_num = Field()
    comment_num = Field()
    
    pass
