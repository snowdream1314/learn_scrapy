# -*- coding: utf-8 -*-
from spider_video.utils.python_mysql import Connection


video_host = "192.168.1.210:3306"
db_video = Connection(host=video_host, database="app_caibo_video", user="caibo_video", password="caibo123")