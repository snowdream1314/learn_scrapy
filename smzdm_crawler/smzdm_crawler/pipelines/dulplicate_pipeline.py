# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem


class DulplicatesPipline(object):
    
    def __init__(self):
        self.ids_seen = set()
        
    def process_item(self, item, spider):
        if item['id'] in self.ids_seen:
            print "Dulplicate item found: %s" % item
            raise DropItem("Dulplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['id'])
            print len(self.ids_seen)
            return item