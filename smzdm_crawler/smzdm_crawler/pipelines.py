# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo


class SmzdmCrawlerPipeline(object):
    
    def __init__(self, mongodb_domain, mongodb_port, mongodb_db):
        self.mongodb_domain = mongodb_domain
        self.mongodb_port = mongodb_port
        self.mongodb_db = mongodb_db
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(mongodb_domain = crawler.settings.get('MONGODB_DOMAIN'),
                   mongodb_port = crawler.settings.get('MONGODB_PORT'),
                   mongodb_db = crawler.settings.get('MONGODB_DB'))
        
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongodb_domain, self.mongodb_port)
        self.db = self.client[self.mongodb_db]
    
    def close_spider(self, spider):
        self.client.close()
                
    def process_item(self, item, spider):
        collection_name = item.__class__.__name__
        self.db[collection_name].insert(dict(item))
        
        return item
