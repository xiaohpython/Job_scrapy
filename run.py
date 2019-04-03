from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.spiderloader import SpiderLoader


# 获取项目配置
settings = get_project_settings()
# 重写配置（当需要存储到数据库时就不用重写配置,将配置进行注释掉就行了）
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
settings.set('USER_AGENT', user_agent, priority='cmdline') # UserAgent
settings.set('FEED_FORMAT', 'json', priority='cmdline') # 结果数据的格式
settings.set('FEED_URI', 'result.json', priority='cmdline') # 数据结果地址
# 爬虫进程
process = CrawlerProcess(settings=settings)
# 爬虫加载器
loader = SpiderLoader.from_settings(settings)
# loader.list() 可以爬取到项目中的 爬虫名称 列表
# 遍历每一个爬虫
for spider_name in loader.list():
    print(spider_name)
    # 得到爬虫类
    SpiderClass = loader.load(spider_name)
    # 得到存储地址(当数据需要存到数据库时这里注释)
    feed_uri = 'result-{}.json'.format(spider_name)
    # 重写当前爬虫的数据存储地址
    settings.set('FEED_URI', feed_uri, priority='cmdline')
    # 添加爬虫任务
    process.crawl(SpiderClass)
# 启动爬虫进程
process.start()
