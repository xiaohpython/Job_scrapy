#### 1.注意：tinydb存入中文,在文件中看到的是Bytes类型,但是不影响读取数据，因为读取数据时不是Bytes，是中文原型

#### 2.当使用 scrapy 的parse方法 换行符导致数据丢失时，
    ```python
        from scrapy import Selector
        # 重新调整response 请求到的数据
        resp = Selector(None, response.body_as_unicode().replace('\r','').replace('\n',''), 'html')
        
    ```