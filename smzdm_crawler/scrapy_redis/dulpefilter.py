# -*- coding: utf-8 -*-
import time

import redis
from scrapy.dupefilters import BaseDupeFilter
from scrapy.utils.request import request_fingerprint


class RFPDupeFilter(BaseDupeFilter):
    """Redis-based duplication filter"""
    
    def __init__(self, server, key):
        """Initialize duplication filter

        Parameters
        ----------
        server : Redis instance
        key : str
            Where to store fingerprints
        """
        
        self.server = server
        self.key = key
    
        
    @classmethod
    def from_settings(cls, settings):
        host = settings.get('REDIS_HOST', 'localhost')
        port = settings.get('REDSIS_PORT', 6379)
        server = redis.Redis(host, port)
        
        key = "dupefilter:%s" % int(time.time())
        
        return cls(server, key)
    
    
    @classmethod    
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)
    
    
    def request_seen(self, request):
        """
            use sismember judge whether fp is dupefilter
        """
        fp = request_fingerprint(request)
        if self.server.sismember(self.key, fp):
            return True
        self.server.sadd(self.key, fp)
        return False
    
    
    def close(self, reason):
        """Delete data on close. Called by scrapy's scheduler"""
        self.clear()
        
        
    def clear(self):
        """clear fingerprints data"""
        self.server.delete(self.key)
        

