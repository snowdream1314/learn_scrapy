# -*- coding: utf-8 -*-
from scrapy.spiders import Spider

from spider_video.conf.config import db_video
from spider_video.utils.load_content import load_content


class youku_video_spider(Spider):
    
    name = "youku"
    allowed_domains = "baidu.com"
    start_urls = ["http://www.baidu.com/"]
    
    def parse(self, response):
        print "parse"
        
#         self.parse_category()
        self.parse_item()
        
    def parse_category(self):
        print "parse_category"
        
        url = "http://www.youku.com/v_showlist"
        
        selector = load_content(url, method='GET')
        if selector is None: return
        
        category_lists = selector.find("div", {"class":"item item-moreshow"}).find("ul").findAll("li", {"class":None})
        for category_list in category_lists:
            name = category_list.find("a").get_text()
            href = "http://www.youku.com" + str (category_list.find("a").attrs['href'])
            print name
            print href
            db_video.insert("cv_video_category", c_name=name, c_href=href)
        db_video.commit()
        
        
    def parse_item(self):
        print "parse_item"
        
        sources = db_video.query("select * from cv_video_category order by c_id  asc")
        for source in sources:
            category_id = source['c_id']
            category_name = source['c_name']
            category_href = source['c_href']
            print category_name
            if category_id == 2:
                self.parseCo13(category_id, category_name, category_href)
            #分为两类不同结构
#             if category_id in [2, 4, 6, 8, 12, 14]:
#                 if category_id == 2: continue
#                 if category_id == 4: continue
#                 self.parseCo13(category_id, category_name, category_href)
#             else:
#                 self.parseCo14(category_id, category_name, category_href)
                
                
    def parseCo13(self, category_id, category_name, category_href):
        print "parseCo13"
        
        source_url = category_href
        while 1:
            
            print source_url
            
            selector = load_content(source_url, method='GET')
            if selector is None: return
            
            lists = selector.findAll("div", {"class":"p p-small"})
            for list in lists:
                #图片链接
#                 img_link = list.find("div", {"class":"p-thumb"}).find("img").attrs['src']
                
                #主角
#                 if list.find("span", {"class":"p-actor"}):
#                     actor_def = list.find("span", {"class":"p-actor"})
#                     actor = actor_def.find("label").get_text().strip() + actor_def.find("a").get_text().strip()
#                     actor_link = actor_def.find("a").attrs['href']
#                 else:
#                     actor = ''
#                     actor_link = ''
#                 print actor
                 
                #资源标示
#                 item_id = item_link.split('_')[-1].split('.')[0]
#                 print "Grab item %s:" % item_id

                #更新情况
#                 update_status = list.find("div", {"class":"p-thumb-taglb"}).find("span", {"class":"p-status"}).get_text().strip()

                #特别标签，如“会员免费”
                if list.find("div", {"class":"p-thumb-tagrt"}) is not None and list.find("div", {"class":"p-thumb-tagrt"}).find("span", {"class":"sub-txt"}) is not None:
                    authority = list.find("div", {"class":"p-thumb-tagrt"}).find("span", {"class":"sub-txt"}).get_text()
                else:
                    authority = "free"
                    
                #资源标题
                item_name = list.find("div", {"class":"p-meta-title"}).find("a").attrs['title']
                print item_name
                    
                #评分
                rating = list.find("div", {"class":"p-thumb-tagrb"}).find("span", {"class":"p-rating"}).get_text().strip()
                
                #资源链接
                item_link = list.find("div", {"class":"p-link"}).find("a").attrs['href']
                
                item_selector = load_content(item_link, method='GET')
                
                videos = db_video.query("select * from cv_video_album where va_video_id=%s", item_id)
                if len(videos) == 0:
                    db_video.insert("cv_video_album", va_category_id=category_id, va_video_id=item_id, va_img_link=img_link, va_name=item_name, va_played_num=played_num, va_video_actor=actor, va_actor_link=actor_link, va_video_link=item_link, va_update_status=update_status, va_video_rate=rating, va_authority=authority )
                    print "insert successfully"
                else:
                    print "video already exists"
                    continue
            db_video.commit()
            
            next_page = selector.find("div", {"class":"yk-pager"}).find("li", {"class":"next"}).find("a")
            if next_page:
                next_link = next_page.attrs['href']
                source_url = "http://www.youku.com" + str(next_link)
            else:
                print "crawled over,category_id is %s:" % category_id
                return
                
        
        
        pass
    
    
    def parseCo14(self, category_id, category_name, category_href):
        
        selector = load_content(category_href, method='GET')
        if selector is None: return
        pass
                