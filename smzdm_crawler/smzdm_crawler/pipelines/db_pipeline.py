# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import redis
from scrapy.exceptions import DropItem


class SmzdmCrawlerPipeline(object):
    
    def __init__(self, mongodb_domain, mongodb_port, mongodb_db, redis_domain, redis_port):
        self.mongodb_domain = mongodb_domain
        self.mongodb_port = mongodb_port
        self.mongodb_db = mongodb_db
        self.redis_domian = redis_domain
        self.redis_port = redis_port
#         self.ids_seen = set()
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(mongodb_domain = crawler.settings.get('MONGODB_DOMAIN'),
                   mongodb_port = crawler.settings.get('MONGODB_PORT'),
                   mongodb_db = crawler.settings.get('MONGODB_DB'),
                   redis_domain = crawler.settings.get('REDIS_DOMAIN'),
                   redis_port = crawler.settings.get('REDIS_PORT'))
        
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongodb_domain, self.mongodb_port)
        self.db = self.client[self.mongodb_db]
        
        self.server = redis.Redis(self.redis_domian, self.redis_port)
        self.redis_key = spider.name
    
    def close_spider(self, spider):
        self.client.close()
                
    def process_item(self, item, spider):
        collection_name = item.__class__.__name__
#         if item['id'] in self.ids_seen:
        if self.server.sismember(self.redis_key, item['id']):
            raise DropItem("dulplicate item found: %s" % item)
        else:
#             self.ids_seen.add(item['id'])
#             print len(self.ids_seen)
            self.server.sadd(self.redis_key, item['id'])
            self.db[collection_name].insert(dict(item))
        
            return item

