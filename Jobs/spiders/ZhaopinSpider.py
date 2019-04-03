# -*- coding: utf-8 -*-
import scrapy
from ..items import JobsItem
from .. import settings

import json
import os
import chardet
try:
    from furl import furl
    from tinydb import TinyDB, Query
except ImportError:
    os.system('pip install tinydb')
    os.system('pip install furl')
    from tinydb import TinyDB, Query
    from furl import furl


class ZhaopinspiderSpider(scrapy.Spider):
    name = 'ZhaopinSpider'
    allowed_domains = ['www.zhaopin.com', 'sou.zhaopin.com', 'fe-api.zhaopin.com']
    start_urls = ['https://www.zhaopin.com/citymap']
    cache_db = TinyDB('ZhaopinSpider-cache.json') # 缓存数据
    allowed_cities = settings.ALLOWED_CITY # 允许的城市(来自settings文件中的设置)
    F = furl('https://fe-api.zhaopin.com/c/i/sou?pageSize=90&kt=3') # url母版
    PAGE_SIZE = 90 # 分页大小


    def get_city_code(self, city_name):
        ''' 根据城市名称获取城市码'''
        Q = Query()
        # import ipdb;ipdb.set_trace()
        city = self.cache_db.get(Q.name.search(city_name))
        if isinstance(city, dict):
            return city['code']
        else:
            print('@'*100)
            print(type(city))


    def init_city_info(self, response):
        '''初始化城市信息'''
         # 获取源码
        script_text = response.xpath('//script[text()[contains(., "__INITIAL_STATE__")]]/text()').extract_first()
        # 去除收尾空白字符
        script_text = script_text.strip()
        # 预处理符合json规范的数据
        script_json = script_text[script_text.index('=') + 1:]
        # 将json转成字典
        script_dict = json.loads(script_json)
        # 将字典中的城市添加到tinydb中
        for ch in script_dict['cityList']['cityMapList']:
            for city in script_dict['cityList']['cityMapList'][ch]:
                self.cache_db.insert(city)


    def parse(self, response):
        # if not os.path.exists('ZhaopinSpider-cache.json'):
        if not bool(self.cache_db.all()): #判断之前是否有数据
            self.init_city_info(response)
        # 迭代每一个要爬取的城市
        for city_name in self.allowed_cities:
            # 爬取允许的所有城市中某一个城市
            yield self.request_city(city_name)

    def request_city(self, city_name, page_start=0):
        ''' 构造 爬取某个具体城市 的请求对象 '''
        city_code = self.get_city_code(city_name)
        url_data = {
            'cityId': city_code,
            'kw': 'python',
            'start': page_start
        }
        # 要爬取的页面的url
        url = self.F.copy().add(url_data).url
        req = scrapy.Request(url, callback=self.parse_city, dont_filter=False)
        # 使用 meta 传递附加数据，在callback中可以通过 respo。meta 取得
        req.meta['city_name'] = city_name
        req.meta['page_start'] = page_start
        return req


    def parse_city(self, response):
        ''' 解析具体的页面 '''
        # 解析json格式的响应结果
        # import ipdb;ipdb.set_trace()
        encoding = chardet.detect(response.body)['encoding']
        resp_dict = json.loads(response.body, encoding=encoding)
        # 总共能爬取的条数
        num_found = resp_dict['data']['numFound']
        # 获取当前请求的 page_start
        page_start = response.meta['page_start']
        # 下一次请求，需要的 start 参数
        next_start = page_start + self.PAGE_SIZE
        # 判断是否有下一页
        if next_start < num_found:
            # 获取当前城市的名称
            city_name = response.meta['city_name']
            # 发送下一页请求
            yield self.request_city(city_name, page_start=next_start)
        # 解析数据
        for item in resp_dict['data']['results']:
            # 解析数据 只取我们需要的信息
            item_item = JobsItem()
            jobName = item['jobName'] #职位名称
            link = item['company']['url'] #公司链接
            salary = item['salary'] # 薪资范围
            address_area = item['city']['display'] # 所属区域
            edu_background = item['eduLevel']['name'] # 教育背景
            work_experience = item['workingExp']['name'] # 工作经验
            company = item['company']['name'] # 公司名称
            company_link = item['company']['url'] # 公司链接

            item_item['jobName'] =jobName
            item_item['source'] = self.name # 来源站点
            item_item['link'] = link
            item_item['salary'] = salary
            item_item['address_area'] = address_area
            item_item['edu_background'] = edu_background
            item_item['work_experience'] = work_experience
            item_item['company'] = company
            item_item['company_link'] = company_link
            yield item_item
            