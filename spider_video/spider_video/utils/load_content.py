# -*- coding: utf-8 -*-
import random
import time

from bs4 import BeautifulSoup
import httplib2


def load_content(url, time_sleep=False, cookie='', method='GET', headers=None):
    print "load_content"
    
    if time_sleep:
        time.sleep(random.randint(1,3))
        
    if headers is None:
        useragent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36"
        headers = {"User-Agent":useragent, "Upgrade-Insecure-Requests":"1", "Cookie":cookie, "Host":"www.youku.com"}
        
    try:
        h = httplib2.Http()
        response, content = h.request(url, method='GET', headers=headers)
        print str(response.status)
        if response.status == 200:
            return BeautifulSoup(content)
        else:
            return None
        
    except Exception,e:
        print str(e)