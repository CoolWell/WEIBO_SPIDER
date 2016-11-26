from scrapy import cmdline
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from Sina_spider1.spiders import spiders
import time
from datetime import timedelta, datetime
import data_handle

seconds_per_day = 24*60*60
while True:
    curTime = datetime.now()
    print 'current time:'+str(curTime)
    desTime = curTime.replace(hour=0, minute=0, second=1, microsecond=0)
    delta = desTime - curTime
    skipSeconds = delta.total_seconds()+seconds_per_day
    print 'skip seconds:%d' % skipSeconds
    time.sleep(skipSeconds)
    process = CrawlerProcess(settings=get_project_settings())
    process.crawl(spiders.Spider)
    process.start()
    process.join()
    data_handle.data_handle()
# cmdline.execute("scrapy crawl sinaSpider".split())

