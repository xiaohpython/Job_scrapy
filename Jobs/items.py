# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    jobName = scrapy.Field() # 职位名称
    source = scrapy.Field() # 来源站点
    link = scrapy.Field() # 公司链接
    salary = scrapy.Field() # 薪资范围
    address_area = scrapy.Field() # 所属区域
    edu_background = scrapy.Field() # 教育背景
    work_experience = scrapy.Field() # 工作经验
    company = scrapy.Field() # 公司名称
    company_link = scrapy.Field() # 公司链接

    

    