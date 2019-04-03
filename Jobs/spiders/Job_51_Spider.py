# -*- coding: utf-8 -*-
import scrapy
from ..items import JobsItem

import re
import os
import time
try:
    from tinydb import TinyDB, Query
except ImportError:
    os.system('pip install tinydb')
    from tinydb import TinyDB, Query
#自定义的防反爬的驱动函数
from ..webdriver_chrome import gen_browser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
        TimeoutException,
        WebDriverException,
        NoSuchElementException,
        StaleElementReferenceException, 
    )

class Job51SpiderSpider(scrapy.Spider):
    name = 'Job_51_Spider'
    allowed_domains = ['www.51job.com','search.51job.com']
    start_urls = ['https://www.51job.com/']
    cache_db = TinyDB('Job_51_Spider-cache.json') # 缓存城市信息


    def parse(self, response):
        driver_path = self.settings.get('DRIVER_PATH')
        browser = gen_browser(driver_path) # 启动webdrider.exe

        # 发起请求 获取页面
        browser.get(response.url)
        try:
            #最多等待 8 秒（选择页面上的地点选项,用于点击进行选择城市）
            _element = WebDriverWait(browser, 8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "p#work_position_click"))
                )
        except (TimeoutException,WebDriverException,NoSuchElementException,StaleElementReferenceException):
            import ipdb; ipdb.set_trace()
            browser.quit()
            
        # 判断缓存文件中是否 有数据
        if not bool(self.cache_db.all()):
            # 执行 获取城市码 的函数 添加缓存文件内容
            self.get_city_name_and_code(response, browser)
            
        # 在主页面 直接点击搜索 进入所有工作列表页面
        browser.find_elements_by_css_selector('div.fltr div.ush button')[0].click()        
        allowed_cities = self.settings.get('ALLOWED_CITY') # 获取允许城市
        want_jobs = self.settings.get('WANT_JOB') # 获取想要的工作        
        # 循环工作和城市
        for job in want_jobs:
            for a_city in allowed_cities:
                # 从缓存文件中获取城市信息
                Q = Query() # 实例化 tinydb 数据的查询
                # 将允许的城市名称放入 查询中,查出该允许城市的城市码
                # import ipdb;ipdb.set_trace()
                a_city_code = self.cache_db.get(Q.name.search(a_city))['code']
                # 写一段js 进行修改地址和工作的值
                js =f'''
                    var job = document.querySelector('input#kwdselectid');
                    //获取城市码的标签
                    var address_code = document.querySelector('input#jobarea');
                    job.value = "{job}"
                    address_code.value = "{a_city_code}"
                    //点击搜索
                    document.querySelector('div.dw_search_in button').click()
                '''
                browser.execute_script(js) # 执行js 修改地址和工作
                # 修改之后要进行点击搜索 才会修改
                browser.find_element_by_css_selector('div.dw_search_in button').click()
                # 取得该页面（下一页地方）的页面总条数
                page_total = int(re.findall('\d+', browser.find_elements_by_css_selector('div.p_in span.td:nth-of-type(1)')[0].text)[0])
                for page in range(1,page_total+1): # 根据页面总条数进行循环
                    # import ipdb ; ipdb.set_trace()
                    page_num = browser.find_elements_by_css_selector('input#jump_page')[0] # 获取页码输入框
                    page_num.clear() # 清空页码输入框
                    page_num.send_keys(page) # 输入页码
                    browser.find_elements_by_css_selector('div.p_in span.og_but')[0].click() # 输入页码之后点击确定
                    # 获取每一工作条目 集合
                    jobs_set = browser.find_elements_by_css_selector('div#resultList div.el+div.el')
                    for job_a in jobs_set:
                        try:
                            all_a_tag = job_a.find_elements_by_xpath('./p/span/a')[0]
                        except Exception:
                            continue
                        link = all_a_tag.get_attribute('href')
                        # import ipdb;ipdb.set_trace()
                        all_a_tag.click() # 每条链接进行点击
                        time.sleep(0.3)
                        num=browser.window_handles #获取浏览器所有标签句柄
                        # import ipdb ; ipdb.set_trace()
                        browser.switch_to_window(num[1]) # 指定调到新标签
                        try:
                            jobName = browser.find_elements_by_css_selector('div.tHeader.tHjob h1')[0].text.strip()
                        except IndexError:
                            browser.close()
                            browser.switch_to_window(num[0])
                            continue
                        source = self.name
                        try:
                            #最多等待 8 秒（选择页面上的地点选项,用于点击进行选择城市）
                            _element = WebDriverWait(browser, 3).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.tHeader.tHjob strong"))
                                )
                        except (TimeoutException,WebDriverException,NoSuchElementException,StaleElementReferenceException):
                            browser.close()
                            browser.switch_to_window(num[0])
                            continue
                        salary =  browser.find_elements_by_css_selector('div.tHeader.tHjob strong')[0].text.strip()[:-2:]
                        try:
                            #最多等待 8 秒（选择页面上的地点选项,用于点击进行选择城市）
                            _element = WebDriverWait(browser, 3).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.cn p.msg"))
                                )
                        except (TimeoutException,WebDriverException,NoSuchElementException,StaleElementReferenceException):
                            browser.close()
                            browser.switch_to_window(num[0])
                            continue
                        address_area = browser.find_elements_by_css_selector('div.cn p.msg')[0].text.split('|')[0].strip()
                        edu_background = browser.find_elements_by_css_selector('div.cn p.msg')[0].text.split('|')[2].strip()
                        work_experience = browser.find_elements_by_css_selector('div.cn p.msg')[0].text.split('|')[1].strip()
                        # import ipdb;ipdb.set_trace()
                        company = browser.find_elements_by_css_selector('div.cn p.cname a:nth-of-type(1)')[0].get_attribute('title').strip()
                        company_link = browser.find_elements_by_css_selector('div.cn p.cname a:nth-of-type(1)')[0].get_attribute('href')
                        print('*'*80)
                        print(jobName)
                        print('*'*80)
                        
                        browser.close()
                        item = JobsItem()
                        item['jobName'] = jobName
                        item['source'] = source
                        item['link'] = link
                        item['salary'] = salary
                        item['address_area'] = address_area
                        item['edu_background'] = edu_background
                        item['work_experience'] = work_experience
                        item['company'] = company
                        item['company_link'] = company_link
            
                        yield item
                        browser.switch_to_window(num[0]) # 切换回主页 的标签
                    


    def get_city_name_and_code(self, response, browser):
        # import ipdb;ipdb.set_trace()
        #  点开所有城市信息的摸态框 目的是获取城市码
        browser.find_element_by_css_selector('p#work_position_click').click()
        # 获取左边城市首字母区域 行数
        city_initial_count = len(browser.find_elements_by_css_selector('ul#work_position_click_center_left li+li'))-2
        # 根据首字母 行数进行循环点击首字母区域 列举出右边的所有城市 找到城市码
        for x in range(1,city_initial_count+1):
            try:
                #最多等待 8 秒（选择页面上的地点选项,用于点击进行选择城市）
                _element = WebDriverWait(browser, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f"ul#work_position_click_center_left li:nth-of-type({(x+1)})"))
                    )
            except (TimeoutException,WebDriverException,NoSuchElementException,StaleElementReferenceException):
                continue
            lis = browser.find_elements_by_css_selector(f'ul#work_position_click_center_left li:nth-of-type({(x+1)})')[0]
            lis.click() # 首字母区域进行点击
            li_id_all = lis.get_attribute('id') # 完整id
            li_id_num = re.findall('\d+', li_id_all)[0] # id的数字部分
            #寻找右边区域 id对应的div            
            city_list_div = browser.find_elements_by_css_selector(f'div#work_position_click_center_right_list_{li_id_num}')[0]
            # 找到div 下的所有city元素
            city_list_all_ele = city_list_div.find_elements_by_css_selector('em')
            for city in city_list_all_ele:
                city_name_and_code = {} # 定义城市信息字典
                city_code = city.get_attribute('data-value')  # 获取城市码
                city_name = city.text.strip() # 获取城市名称
                city_name_and_code['name'] = city_name
                city_name_and_code['code'] = city_code # 以城市名称作为键,城市码作为值
                # import ipdb;ipdb.set_trace()
                self.cache_db.insert(city_name_and_code) # 将得到的数据添加到缓存文件中
        # 关闭摸态框（获取缓存数据完成之后）
        browser.find_elements_by_css_selector('div#work_position_click_init h2 a')[0].click()
      
                