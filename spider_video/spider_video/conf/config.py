# -*- coding: utf-8 -*-
import redis

from spider_video.utils.python_mysql import Connection


redisdb = redis.Redis(host="localhost", port=6379, db=0)

video_host = "192.168.1.210:3306"
db_video = Connection(host=video_host, database="app_caibo_video", user="caibo_video", password="caibo123")