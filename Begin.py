from scrapy import cmdline
from apscheduler.schedulers.blocking import BlockingScheduler
import logging


# def job_period():
cmdline.execute("scrapy crawl sinaSpider".split())

# if __name__ == '__main__':
#     logging.basicConfig()
#     sched = BlockingScheduler()
#     sched.add_job(job_period, 'cron', start_date='2016-09-01', hour=10, minute=13, second=1, end_date='2016-11-30')
#     a = sched.get_jobs()
#     print(a)
#     sched.start()