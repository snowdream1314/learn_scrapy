# -*- coding: utf-8 -*-
import redis
from scrapy.utils.misc import load_object
from scrapy_redis.dupefilter import RFPDupeFilter


#default values
QUEUE_KEY = '%(spider)s:requests'
QUEUE_CLASS = '.queue.SpiderPriorityQueue'
DUPEFILTER_KEY = '%(spider)s:dupefilter'
SCHEDULER_PERSIST = False
IDLE_BEFORE_CLOSE = 0

class Scheduler(object):
    """Redis-based scheduler"""
    
    
    def __init__(self, server, persist, queue_cls, queue_key, dupefilter_key, idle_before_close):
        """Initialize scheduler.
        
        Parameters:
        -----------
            server: redis instance
            persist: bool
            queue_cls: queue class
            queue_key: str
            dupefilter_key: str
            idle_before_close: int
        """
        
        self.server = server
        self.persist = persist
        self.queue_cls = queue_cls
        self.queue_key = queue_key
        self.dupefilter_key = dupefilter_key
        self.idle_before_close = idle_before_close
        self.status = None
        
    
    def __len__(self):
        return len(self.queue)
        
        
    @classmethod
    def from_settings(cls, settings):
        persist = settings.get('SCHEDULER_PERSIST', SCHEDULER_PERSIST)
        host = settings.get('REDIS_HOST', 'localhost')
        port = settings.get('REDIS_PORT', 6379)
        server = redis.Redis(host, port)
        queue_key = settings.get('SCHEDULER_QUEUE_KEY', QUEUE_KEY)
        queue_cls = load_object(settings.get('SCHEDULER_QUEUE_CLASS', QUEUE_CLASS))
        idle_before_close = settings.get('SCHEDULER_IDLE_BEFORE_CLOSE', IDLE_BEFORE_CLOSE)
        dupefilter_key = settings.get('DUPEFILTER_KEY', DUPEFILTER_KEY)
        return cls(server, persist, queue_cls, queue_key, dupefilter_key, idle_before_close)
        
    
    @classmethod
    def from_crawler(cls, crawler):
        instance = cls.from_settings(crawler.settings)
        # FIXME: for now, stats are only supported from this constructor
        instance.stats = crawler.stats
        return instance
#         settings = crawler.settings
#         return cls.from_settings(settings)
    
    
    def open(self, spider):
        """
            execute this function when open one spider
        """
        
        self.spider = spider
        self.queue = self.queue_cls(self.server, spider, self.queue_key)
        self.dupefilter = RFPDupeFilter(self.server, self.dupefilter_key % {'spider':spider.name})
        if self.idle_before_close < 0:
            self.idle_before_close = 0
        # notice if there are requests already in the queue to resume the crawl
        if len(self.queue):
            spider.log("Resuming crawl (%d requests scheduled)" % len(self.queue))
        print "++++++++++++++++++++++++"
        print  "scheduler open"
        print "++++++++++++++++++++++++"
        
    
    def close(self, reason):
        if not self.persist:
            self.dupefilter.clear()
            self.queue.clear()
        print "++++++++++++++++++++++++"
        print "scheduler close"
        print "++++++++++++++++++++++++"
    
    
    def enqueue_request(self, request):
        if not request.dont_filter and self.dupefilter.request_seen(request):
            return 
#         if self.stats:
        self.stats.inc_value('scheduler/enqueued/redis', spider=self.spider)
        self.queue.push(request)
        print "++++++++++++++++++++++++" 
        print "scheduler, push request"
        print "++++++++++++++++++++++++"
        
    
    def next_request(self):
        print "++++++++++++++++++++++++"
        print "scheduler next_request"
        print "++++++++++++++++++++++++"
        request = self.queue.pop()
        if request:
           self.stats.inc_value('scheduler/enqueued/redis', spider=self.spider) 
        return request
    
    
    def has_pending_requests(self):
        return len(self) > 0
      
    