# -*- coding: utf-8 -*-
import scrapy
from ..items import JobsItem

import time

class HuibospiderSpider(scrapy.Spider):
    name = 'HuiboSpider'
    allowed_domains = ['www.huibo.com/']
    start_urls = ['http://www.huibo.com/jobsearch/?key=php']

    def parse(self, response):
        # import ipdb;ipdb.set_trace()
        # 取得所有工作的列表 的链接
        job_list_url = response.css('div.postIntroL div.postIntroLx p span.name').xpath('.//a/@href').extract()
        # 下一页
        next_page = response.xpath('//div[@class="page"]/a[text()[contains(.,"下一页")]]/@href').extract_first()
        # 遍历每一个工作
        for url in job_list_url:
            # 将每个工作的链接作为新的访问地址 抛给parse_detail函数访问处理
            yield scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
        if bool(next_page):
            yield scrapy.Request(url=next_page, callback=self.parse, dont_filter=True)
            

    def parse_detail(self, response):
        """ 解析数据 并存储 """
        # time.sleep(1)
        # import ipdb;ipdb.set_trace()
        try:            
            jobName = response.xpath('//div[@class="newJobtop"]/div[@class="newtopTit"]/h2/text()').extract_first().strip()
            print(jobName)
            link =response.url
            salary = response.xpath('//div[@class="newJobDtl"]/p[1]/span/text()').extract_first().strip()[1:-1:].split('\r')[0].replace('\n', '')
            area = response.xpath('//div[@class="newJobDtl"]/p[3]/span[1]/a/text()').extract_first().strip()
            address = response.xpath('//div[@class="newJobDtl"]/p[3]/span[1]/text()').extract_first().strip()
            address_area = area + address # 拼接成地区加具体地址
            edu_background = response.xpath('//div[@class="newJobDtl"]/p[2]/span[1]/text()').extract_first().strip().split('/')[0].strip()
            work_experience = response.xpath('//div[@class="newJobDtl"]/p[2]/span[1]/text()').extract_first().strip().split('/')[1].strip()
            company = response.xpath('//div[@class="newJobBg"]/div[@class="newJobLf"]/div[@class="newJobtop"]/p/span/a/text()').extract_first().strip()
            company_link = response.xpath('//div[@class="newJobBg"]/div[@class="newJobLf"]/div[@class="newJobtop"]/p/span/a/@href').extract_first().strip()

            item = JobsItem()
            item['jobName'] = jobName
            item['source'] = self.name
            item['link'] = link
            item['salary'] = salary
            item['address_area'] = address_area
            item['edu_background'] = edu_background
            item['work_experience'] = work_experience
            item['company'] = company
            item['company_link'] = company_link
            yield item
        except Exception as e:
            pass

