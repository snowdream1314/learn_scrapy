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
            if category_id == 8:
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
                print ''
                print "++++++++++++++++++++++++++++++++++++++++++++++++++"
                print ''
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
                print "---------------------------------"
                video_name = list.find("div", {"class":"p-meta-title"}).find("a").attrs['title']
                print video_name
                print "----------------------------------" 
                print ''   
                #评分
                video_rating = list.find("div", {"class":"p-thumb-tagrb"}).find("span", {"class":"p-rating"}).get_text().strip()
                
                #资源链接
                video_link = list.find("div", {"class":"p-link"}).find("a").attrs['href']
                video_id = video_link.split("id_z")[-1].split(".")[0]
                
                item_selector = load_content(video_link, method='GET')
                if item_selector is None: return
                
                item_showInfo = item_selector.find("div", {"class":"showInfo poster_w yk-interact"}).find("ul", {"class":"baseinfo"})
                item_basedata = item_selector.find("div", {"class":"showInfo poster_w yk-interact"}).find("ul", {"class":"basedata"})
                item_basenotice = item_selector.find("div", {"class":"showInfo poster_w yk-interact"}).find("div", {"class":"basenotice"})
                
                #播放链接,视频id
                show_link = item_showInfo.find("li", {"class":"link"}).find("a")
                if show_link is not None:
                    show_link = show_link.attrs['href']
                else:
                    show_link = item_selector.find("ul", {"class":"baseaction"}).find("li", {"class":"action"}).find("a").attrs['href']
#                 video_id = show_link.split('from=')[-1].split('.')[-1]
                print "video_id is : %s" % video_id
                
                #豆瓣评分
                score_db = item_selector.find("div", {"class":"showInfo poster_w yk-interact"}).find("div", {"class":"score_db score_db_btn"})
                if score_db is not None:
                    score_db = score_db.find("span").get_text()
                else:
                    score_db = ''
                #图片链接
                img_link = item_showInfo.find("li", {"class":"thumb"}).find("img").attrs['src']
                
                #视频画质
#                 video_quality = item_showInfo.find("li", {"class":"ishd"}).find("span").attrs['class'].split('__')[-1]
#                 print "quality is : %s" % video_quality
                
                #视频别名
                video_alias = item_showInfo.find("span", {"class":"alias"})
                if video_alias is not None:
                    video_alias = video_alias.attrs['title']
                else:
                    video_alias = ''
                print "video_alias is : %s" % video_alias
                
                #视频时长
                video_duration = item_showInfo.find("span", {"class":"duration"}) 
                if video_duration is not None:
                    video_duration = video_duration.get_text().split(":")[-1].replace("\n", "").replace("\t", "").replace("\r", "").strip()
                else:
                    video_duration = ''
                print "video_duration is : %s" % video_duration
                
                #上映时间和优酷上映时间
                time_items = item_showInfo.findAll("span", {"class":"pub"}) 
                if len(time_items) == 1:                                                                                               
                    show_time = time_items[0].get_text().split(":")[-1].replace("\n", "").replace("\t", "").replace("\r", "").strip()
                    yk_showtime = ''
                elif len(time_items) == 2:   
                    show_time = time_items[0].get_text().split(":")[-1].replace("\n", "").replace("\t", "").replace("\r", "").strip()
                    yk_showtime = time_items[1].get_text().split(":")[-1].replace("\n", "").replace("\t", "").replace("\r", "").strip() 
                else:
                    show_time = ''
                    yk_showtime = ''
                print "show_time is : %s" % show_time
                print "yk_showtime is : %s" % yk_showtime
                
                #地区和类型
                video_area = item_showInfo.find("span", {"class":"area"}).find("a").get_text()
                video_type = item_showInfo.find("span", {"class":"type"}).attrs['title']
                print video_area, video_type
                
                #导演和主演
                video_director = item_showInfo.find("span", {"class":"director"})
                if video_director is None:
                    video_director = item_showInfo.find("span", {"class":"host"})
                if video_director is not None and video_director.find("a") is not None:
                    video_director = video_director.find("a").get_text()
                else:
#                     if list.find("span", {"class":"p-actor"}) is not None:
#                         video_director = list.find("span", {"class":"p-actor"}).find("a").get_text()
#                     else:
                    video_director = ''
                video_actors = item_showInfo.find("span", {"class":"actor"})
                if video_actors is not None and video_actors.find("a") is not None:
                    video_actors = video_actors.attrs['title']
                else:
                    video_actors = ''
                print "director is : %s" % video_director
                print "actors : %s" % video_actors
                
                #动漫的适用年龄
                video_agefor = ''
                if category_id == 8:
                    video_agefor = item_showInfo.find("span", {"class":"actor"}).get_text().split(":")[-1].replace("\n", "").replace("\t", "").replace("\r", "").strip()
                    print "video_agefor is : %s" % video_agefor
                    video_actors_items = item_showInfo.findAll("li", {"class":"row1"})
                    for video_actors_item in video_actors_items:
                        if video_actors_item.find("span", {"class":"type"}) is not None and video_actors_item.find("span", {"class":"type"}).find("a") is not None:
                            video_actors = video_actors_item.find("span").attrs['title']
                            print "actors : %s" % video_actors
                    
                #播出频道
                video_TV = item_showInfo.find("span", {"class":"broadcast"})
                if video_TV is not None:
                    video_TV = video_TV.find("a").get_text()
                else:
                    video_TV = ''
                    
                #总播放量、评论数量、'顶'数量
                played_count = item_basedata.find("span", {"class":"play"}).get_text().split(":")[-1].strip()
                comment_num = item_basedata.find("span", {"class":"comment"}).find("em", {"class":"num"}).get_text().strip()
                support_num = item_basedata.find("span", {"class":"increm"}).get_text().split(":")[-1].strip()
                print "played_count is : %s" % played_count
                print "comment_num is : %s" % comment_num
                print "support_num is : %s" % support_num
                
                #更新状态
                update_schedule = item_basenotice.get_text().replace("\n", "").replace("\t", "").replace("\r", "").strip()
                if len(update_schedule) > 10:
                    update_status = 0
                else:
                    update_status = 1
                print "update_schedule is : %s " % update_schedule
                
                #视频简介
                item_desc = item_selector.find("div", {"class":"box nBox"}).find("div", {"class":"detail"})
                if item_desc is not None:
                    if item_desc.find("span", {"class":"long"}) is not None:
                        video_desc = item_desc.find("span", {"class":"long"}).get_text().replace("\n", "").replace("\t", "").replace("\r", "").strip()
                    elif item_desc.find("span", {"style":True, "class":None}) is not None:
                        video_desc = item_desc.find("span", {"style":True, "class":None}).get_text().replace("\n", "").replace("\t", "").replace("\r", "").strip()
                    else:
                        video_desc = item_desc.find("span", {"class":"short"}).get_text().replace("\n", "").replace("\t", "").replace("\r", "").strip()
                else:
                    video_desc = ''
                print "video_desc is: %s" % (video_desc[:40])
                   
                
#                 videos = db_video.query("select * from cv_video_album where va_video_id=%s", item_id)
                videos = db_video.query("select * from cv_video_detail_msg where cv_video_id=%s", video_id)
                if len(videos) == 0:
#                     db_video.insert("cv_video_album", va_category_id=category_id, va_video_id=item_id, va_img_link=img_link, va_name=item_name, va_played_num=played_num, va_video_actor=actor, va_actor_link=actor_link, va_video_link=item_link, va_update_status=update_status, va_video_rate=rating, va_authority=authority )
                    db_video.insert("cv_video_detail_msg", cv_category_id=category_id, cv_video_name=video_name, cv_video_id=video_id, cv_played_count=played_count, cv_video_desc=video_desc,
                                    cv_video_link=video_link, cv_video_rate=video_rating, cv_video_alias=video_alias, cv_video_area=video_area, cv_video_type=video_type, cv_video_director=video_director,
                                    cv_video_actors=video_actors, cv_comment_num=comment_num, cv_support_num=support_num, cv_update_schedule=update_schedule, cv_video_img=img_link, cv_video_auth=authority,
                                    cv_show_link=show_link, cv_douban_rate=score_db, cv_update_status=update_status, cv_video_duration=video_duration, cv_video_TV=video_TV, cv_video_agefor=video_agefor)
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
                print "crawled over,category_id is : %s" % category_id
                return
                
        
        
        pass
    
    
    def parseCo14(self, category_id, category_name, category_href):
        
        selector = load_content(category_href, method='GET')
        if selector is None: return
        pass
                