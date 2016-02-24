#!/usr/env/bin python
# coding=utf8

"""
单机版

单机的日志 -> 特征的分析系统
输入：归总之后的日志记录， 例如：
55127e5d6bdcdc15558b4c49,click,d7077cd9724043e99166fcd4163ffc8cefa2e1fa,user_id,iphone 6 (a1549/a1586),ios,app_version,667,375,8.1.3,101.80.148.236,1427328061
由逗号分隔，表示数据项有： article_id, shown|click|share, device_id, user_id, device, os, app_version, pixel_wight, pixel_height, OS verion, IP, timestamp

输出两种文件：
1. 特征 -> id的映射文件
2. 指定格式的训练数据文件 （weka, liblinear, vw....）

"""
