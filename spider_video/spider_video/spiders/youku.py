# -*- coding: utf-8 -*-
from urllib import urlencode

from scrapy.spiders import Spider
from selenium import webdriver

from spider_video.conf.config import db_video
from spider_video.utils.load_content import load_content
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup


class youku_video_spider(Spider):
    
    name = "youku"
    
    def __init__(self, update=False):
        self.allowed_domains = "baidu.com"
        self.start_urls = ["http://www.baidu.com/"]
        self.update = update
    
    def parse(self, response):
        print "parse"
        
#         self.parse_category()
        self.parse_item(self.update)
#         self.parseEpisodes(self.update)
        
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
        
        
    def parse_item(self, update=False):
        print "parse_item"
        
        sources = db_video.query("select * from cv_video_category order by c_id  asc")
        for source in sources:
            category_id = source['c_id']
            category_name = source['c_name']
            category_href = source['c_href']
            print category_name
            
#             if category_id == 14:
#                 self.parseCol3(category_id, category_name, category_href, update)
            if category_id == 10:
                self.parseCol4(category_id, category_name, category_href, update)
            #分为两类不同结构
#             if category_id in [2, 4, 6, 8, 12, 14]:
#                 if category_id == 2: continue
#                 if category_id == 4: continue
#                 if category_id == 6: continue
#                 if category_id == 8: continue
#                 if category_id == 12: continue
#                 self.parseCol3(category_id, category_name, category_href, update)
#             else:
#                 self.parseCol4(category_id, category_name, category_href, update)
    
    
    #获取/更新电视剧集
    def parseEpisodes(self, update=False):
        print "parseEpisodes"  
        
        #是否更新
        if update:
            sources = db_video.query("select * from cv_video_detail_msg_copy where cv_update_status=0")
            print "%s videos need to update" % len(sources)
            print "start update"
        else:
            sources = db_video.query("select * from cv_video_detail_msg_copy") 
        
        #从上次停止的地方开始
        last_eopisode = db_video.query("select * from cv_video_episodes order by ve_id DESC LIMIT 0,1")
        last_video = db_video.query("select * from cv_video_detail_msg_copy where cv_video_id=%s", last_eopisode[0]['ve_video_id'])
        print "cv_id is : %s" % last_video[0]['cv_id']
        print  ""
        print "*****************************************************"
        print "last video_name is : %s" % last_eopisode[0]['ve_video_name']
        print "last video_id is : %s" % last_eopisode[0]['ve_video_id']
        print "******************************************************"
        print ""
      
        for source in sources:
            category_id = source['cv_category_id']  
            video_id = source['cv_video_id'] 
            video_name = source['cv_video_name']
            video_href = source['cv_video_link']
            show_link = source['cv_show_link']
            video_cv_id = source['cv_id']
#             if video_cv_id < last_video[0]['cv_id']: continue   #从上次停止的地方开始,更新中断开启
            
            #爬取中断时调试，更新时不可用
#             videos_query = db_video.query("select * from cv_video_episodes where ve_video_id = %s", video_id)
#             if len(videos_query) != 0:
#                 print "%s has grabed" % video_name
#                 continue
            
            if category_id in [2, 4, 6, 8, 12, 14]:
                print ""
                print "+++++++++++++++++++++++++++++++++++++++++++"
                print "grab : %s" % video_name  
                print"++++++++++++++++++++++++++++++++++++++++++++"
                print ""
                
                #准备url参数，以便获取分集加载的json资源链接
                dt="json"
                divid=''
                rt=1
                tab=0
                ro="reload_point"
                params = {"dt":dt, "tab_num":4, "rt":rt, "ro":ro}
                reload_url = "http://www.youku.com/show_point_id_z" + str(video_id) + ".html?" + str(urlencode(params))
                print "reload_url is : %s" % reload_url
                
                reload_selector = load_content(reload_url, method='GET', time_sleep=True)
                seriesTabs = reload_selector.find("ul", {"id":"zySeriesTab"})
                if seriesTabs is not None:
                    point_reloads = seriesTabs.findAll("li", {"data":True})
                    for point_reload in point_reloads:
                        divid = point_reload.attrs['data']
                        ro = point_reload.attrs['data']
                        point_reload_params = {"dt":dt, "divid":divid, "tab":tab, "rt":rt, "ro":ro}
                        
                        point_reload_url = "http://www.youku.com/show_point/id_z" + str(video_id) + ".html?" + str(urlencode(point_reload_params))
                        print "---------------------------------------------------"
                        print "point_reload_url is : %s" % point_reload_url
                        print "---------------------------------------------------"
                        
                        point_reload_selector = load_content(point_reload_url, method='GET', time_sleep=True)
                        episodes = point_reload_selector.findAll("div", {"class":"item"})
                        
                        self.parseEpisodesItems(episodes, video_id, video_name)
                else:
                    episodes = reload_selector.findAll("div", {"class":"item"})
                    self.parseEpisodesItems(episodes, video_id, video_name)
                    
            if update:
                print "%s is updated over" % video_name
            else:
                print "%s is grabed over" % video_name
        
        if update:
            print "all videos are updated over" 
        else:
            print "all videos are grabed over"    
        
        pass 
     
    
    #解析电视剧集具体条目
    def parseEpisodesItems(self, episodes, video_id, video_name):
        print "parseEpisodesItems"
        
        for episode in episodes:
            if episode.find("div", {"class":"link"}) is None: continue
            episode_title = episode.find("div", {"class":"title"}).find("a").get_text().strip()
            try:
                episode_href = episode.find("div", {"class":"link"}).find("a").attrs['href']
                episode_img = episode.find("div", {"class":"thumb"}).find("img").attrs['src']
            except KeyError:
                episode_href = episode.find("div", {"class":"keylist"}).find("a").attrs['href']
                episode_img = ''
                episode_title = episode_title.split(">")[-1]
            episode_id = episode_href.split("id_")[-1].split(".html")[0]
            duration_time = episode.find("div", {"class":"time"}).find("span", {"class":"num"}).get_text() if episode.find("div", {"class":"time"}).find("span", {"class":"num"}) is not None else None
            
            played_count = episode.find("div", {"class":"stat"}).find("span", {"class":"num"}).get_text().replace(",", "").strip() if episode.find("div", {"class":"stat"}) is not None else None
            if played_count is None:
                played_count = 0
            else:
                played_count = int (played_count)
                
            episode_desc = episode.find("div", {"class":"desc"}).get_text().replace("\n", "").replace("\t", "").replace("\r", "").strip()
            print "episode_id is : %s" % episode_id
            print "episode_title is : %s" % episode_title
            print "episode_desc is : %s" % (episode_desc[:40])
            
            episode_querys = db_video.query("select * from cv_video_episodes where ve_episode_id = %s", episode_id)
            if len(episode_querys) == 0:
                db_video.insert("cv_video_episodes", ve_video_id=video_id, ve_video_name=video_name, ve_episode_id=episode_id,
                                 ve_episode_href=episode_href, ve_episode_title=episode_title, ve_episode_duration=duration_time,
                                 ve_episode_img=episode_img, ve_played_count=played_count, ve_episode_desc=episode_desc)
                print "%s insert successfully" % episode_title
            else:
                print " %s already exist" % episode_title
                continue
            
        db_video.commit()
               
            
    def parseCol3(self, category_id, category_name, category_href, update=False):
        print "parseCol3"
        
        source_url = category_href
#         if category_id == 14 :
#             source_url = "http://www.youku.com/v_olist/c_84_g__a__sg__mt__lg__q__s_1_r_0_u_0_pt_0_av_0_ag_0_sg__pr__h__d_1_p_24.html"
        while 1:
             
            print source_url
             
            selector = load_content(source_url, method='GET')
            if selector is None: return
             
            lists = selector.findAll("div", {"class":"p p-small"})
            for list in lists:
                print ''
                print "++++++++++++++++++++++++++++++++++++++++++++++++++"
                print ''
 
                #特别标签，如“会员免费”
                if list.find("div", {"class":"p-thumb-tagrt"}) is not None and list.find("div", {"class":"p-thumb-tagrt"}).find("span", {"class":"sub-txt"}) is not None:
                    authority = list.find("div", {"class":"p-thumb-tagrt"}).find("span", {"class":"sub-txt"}).get_text()
                else:
                    authority = "free"
                     
                #资源标题
                video_name = list.find("div", {"class":"p-meta-title"}).find("a").attrs['title']
                print "---------------------------------"
                print video_name
                print "----------------------------------" 
                print ''  
                 
                #评分
                video_rating = list.find("div", {"class":"p-thumb-tagrb"}).find("span", {"class":"p-rating"}).get_text().replace(".", "").strip()
                if video_rating == '':
                    video_rating = 0
                else:
                    video_rating = int(video_rating)
                    
                #资源链接
                video_link = list.find("div", {"class":"p-link"}).find("a").attrs['href']
                video_id = video_link.split("id_z")[-1].split(".")[0]
                
                #判断是否已经爬取过
                if not update:
                    videos = db_video.query("select * from cv_video_detail_msg_copy where cv_video_id=%s", video_id)
                    if len(videos) != 0 : 
                        print "%s already exist" %video_name
                        continue
                 
                item_selector = load_content(video_link, method='GET', time_sleep=True, referer=category_href)
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
                    score_db = int (score_db.find("span").get_text().replace(".", ""))
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
                if len(time_items) == 1 :                                                                                               
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
                video_area = item_showInfo.find("span", {"class":"area"})
                if video_area is not None and video_area.find("a") is not None:
                    video_area = video_area.find("a").get_text()
                else:
                    video_area = ''
                video_type = item_showInfo.find("span", {"class":"type"})
                if video_type is not None and video_type.find("a") is not None:
                    video_type = video_type.attrs['title']
                else:
                    video_type = ''
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
                     
                if category_id == 12:   #教育类标签不一样
                    video_director = video_area
                    video_area = ''
                if category_id == 14:
                    video_director = item_showInfo.find("li", {"class":"row1", "style":None})
                    if video_director is not None and video_director.find("a") is not None:
                        video_director = video_director.find("a").get_text()
                    else:
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
                played_count = int (item_basedata.find("span", {"class":"play"}).get_text().split(":")[-1].replace(",","").strip())
                comment_num = int (item_basedata.find("span", {"class":"comment"}).find("em", {"class":"num"}).get_text().replace(",","").strip())
                support_num = int (item_basedata.find("span", {"class":"increm"}).get_text().split(":")[-1].replace(",","").strip())
                print "played_count is : %s" % played_count
                print "comment_num is : %s" % comment_num
                print "support_num is : %s" % support_num
                 
                #更新状态
                update_schedule = item_basenotice.get_text().replace("\n", "").replace("\t", "").replace("\r", "").strip()
                if u"更新" in update_schedule:
                    update_status = 0
                else:
                    update_status = 1
                
                if category_id == 4:
                    update_schedule = list.find("div", {"class":"p-thumb-taglb"}).find("span", {"class":"p-status"}).get_text()
                    if u"预告" in update_schedule:
                        update_status = 0
                    else:
                        update_status = 1
                        
#                 if len(update_schedule) > 10:
#                     update_status = 0
#                 else:
#                     update_status = 1
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
                
                #分集剧情，动态改变表的结构，不可取！
#                 episodes = item_selector.find("div", {"class":"box nBox"}).find("div", {"class":"linkpanel"}).findAll("a", {"data-from":True}) 
#                 self.parseEpisodes(category_id, category_name, video_id, video_name, episodes)
#                 for episode in episodes:
#                     episode_href = episode.attrs['href'] 
#                     print "episode_href is : %s" % episode_href
#                     episode_text = episode.get_text()  
#                     db_video.execute("alter table cv_video_detail_msg add episode%s varchar(300)" %episode_text )
#                     print "update cv_video_detail_msg set episode%s=%s where cv_video_id=%s" %(episode_text, episode_href, video_id)
#                     db_video.execute("update cv_video_detail_msg set episode1=%s where cv_video_id=%s", episode_href, video_id)
                    
                videos = db_video.query("select * from cv_video_detail_msg_copy where cv_video_id=%s", video_id)
                if len(videos) == 0:
                    db_video.insert("cv_video_detail_msg_copy", cv_category_id=category_id, cv_video_name=video_name, cv_video_id=video_id, cv_played_count=played_count, cv_video_desc=video_desc,
                                    cv_video_link=video_link, cv_video_rate=video_rating, cv_video_alias=video_alias, cv_video_area=video_area, cv_video_type=video_type, cv_video_director=video_director,
                                    cv_video_actors=video_actors, cv_comment_num=comment_num, cv_support_num=support_num, cv_update_schedule=update_schedule, cv_video_img=img_link, cv_video_auth=authority,
                                    cv_show_link=show_link, cv_douban_rate=score_db, cv_update_status=update_status, cv_video_duration=video_duration, cv_video_TV=video_TV, cv_video_agefor=video_agefor,
                                    cv_show_time=show_time, cv_yk_showtime=yk_showtime)
                    print "%s insert successfully" %video_name
                        
                else:
                    #更新每一部电视剧的信息
                    if update:
                        db_video.execute("update cv_video_detail_msg_copy set cv_played_count=%s, cv_video_rate=%s, cv_comment_num=%s, cv_support_num=%s, \
                                        cv_update_schedule=%s, cv_update_status=%s where cv_video_id=%s", played_count, video_rating, comment_num, support_num, update_schedule, update_status, video_id)
                        print " %s update successfully" % video_name
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
    
    
    def parseCol4(self, category_id, category_name, category_href, update=False):
        
        print "parseCol4"
        
        source_url = category_href
        
        #开启selenium工具，以便后续获取动态数据
#         web_driver = webdriver.Chrome()
        
        while 1:
            
            print source_url
            
            selector = load_content(category_href, method='GET')
            if selector is None: return
            
            lists = selector.findAll("div", {"class":"yk-col4"})
            for list in lists:
                v_thumb = list.find("div", {"class":"v"}).find("div", {"class":"v-thumb"})
                v_link = list.find("div", {"class":"v"}).find("div", {"class":"v-link"})
                v_meta = list.find("div", {"class":"v"}).find("div", {"class":"v-meta va"})
                
                #图片链接
                img_link = v_thumb.find("img").attrs['src']
                
                #视频质量
                video_quality = v_thumb.find("div", {"class":"v-thumb-tagrt"}).find("i")
                if video_quality is not None:
                    video_quality = video_quality.attrs['title']
                    print "video_quality is : %s" % video_quality
                    
                #视频时长
                video_duration = v_thumb.find("div", {"class":"v-thumb-tagrb"}).find("span", {"class":"v-time"})
                if video_duration is not None:
                    video_duration = video_duration.get_text()
                    print "video_duration is : %s" %video_duration
                    
                #视频演员作者
                video_actors = v_thumb.find("div", {"class":"v-thumb-taglb"})
                if video_actors is not None:
                    video_actors = video_actors.find("span", {"class":"v-status"}).get_text().replace("\n", "").replace("\r", "").replace("\t", "").strip()
                elif v_meta.find("a", {"class":"v-username"}) is not None:
                    video_actors = v_meta.find("a", {"class":"v-username"}).get_text().strip()
                else:
                    video_actors = ''
                print "video_actors is : %s" % video_actors
                
                #视频播放链接
                show_link = v_link.find("a").attrs['href']
                video_id = show_link.split("id_")[-1].split(".html")[0]
                print "video_id is : %s" %video_id
                
                #视频标题
                video_name = v_meta.find("div", {"class":"v-meta-title"}).find("a").get_text()
                print "video_name is : %s" % video_name
                
                #获取动态的数据：评论数、支持数、播放数
#                 web_driver = webdriver.Chrome()
                web_driver = webdriver.Firefox()
                print "web_driver"
                #调用浏览器加载页面
                web_driver.get(show_link)
                #等待，直到评论数加载完毕
                WebDriverWait(web_driver,10).until(lambda the_driver: the_driver.find_element_by_id("video_comment_number").get_attribute('title') != '')
                page_soup = BeautifulSoup(web_driver.page_source)
                web_driver.quit()
                
                comment_num = int (page_soup.find("a", {"id":"video_comment_number"}).attrs['title'])
                support_num = int (page_soup.find("div", {"class":"fn-updown"}).find("div", {"class":"fn-up"}).find("span", {"class":"num"}).get_text().strip())
                played_num = page_soup.find("div", {"class":"fn-wrap"}).find("span", {"id":"videoTotalPV"}).get_text().replace(u"播放", "").replace(".", "").replace(",", "").strip()
                if u"万" in played_num:
                    played_count = int (played_num.replace(u"万", "")) * 10000
                else:
                    played_count = int (played_num) 
#                 item_selector = load_content(show_link, method='GET', time_sleep=True, host="v.youku.com")
#                 if item_selector is None: return
                
                #视频支持数
#                 support_num = item_selector.find("div", {"class":"fn-updown"}).find("div", {"class":"fn-up"}).find("span", {"class":"num"}).get_text().strip()
                
                #视频评论数和播放总数,数据动态加载，无法获取
#                 comment_num = item_selector.find("div", {"class":"fn-wrap"}).find("a", {"id":"video_comment_number"}).attrs['title']
#                 played_count = item_selector.find("div", {"class":"fn-wrap"}).find("span", {"id":"videoTotalPV"}).find("em", {"class":"num"}).get_text().replace(",", "").strip()
                print "support_num is : %s" % support_num
                print "comment_num is : %s" % comment_num
                print "played_count is : %s" % played_count
                
                videos = db_video.query("select * from cv_video_detail_msg where cv_video_id=%s", video_id)
                if len(videos) == 0:  
                    db_video.insert("cv_video_detail_msg", cv_category_id=category_id, cv_video_name=video_name, cv_video_id=video_id, cv_played_count=played_count, 
                                    cv_video_actors=video_actors, cv_comment_num=comment_num, cv_support_num=support_num, cv_video_img=img_link, cv_video_auth="free",
                                    cv_show_link=show_link, cv_video_duration=video_duration)
                    print "insert successfully"
                else:
                    print "video already exists"
                    continue
                
#             db_video.commit()
            
            next_page = selector.find("div", {"class":"yk-pager"}).find("li", {"class":"next"}).find("a")
            if next_page:
                next_link = next_page.attrs['href']
                source_url = "http://www.youku.com" + str(next_link)
            else:
                print "crawled over,category_id is : %s" % category_id
                return
            
#         web_driver.quit()
                
        pass
                