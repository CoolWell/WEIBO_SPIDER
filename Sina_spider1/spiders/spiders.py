# encoding=utf-8
import re
import datetime
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from Sina_spider1.items import InformationItem, TweetsItem, FollowsItem, FansItem, CommentItem, RepostItem
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Spider(CrawlSpider):
    name = "sinaSpider"
    host = "http://weibo.cn"
    with open('10000.txt') as f:
        start_urls = f.readlines()
    for index, value in enumerate(start_urls):
        start_urls[index] = value.strip('\n')
    # print(len(start_urls))
    # start_urls = [
    #      1642634100, 1376234365, 3069348215,
    #      2684399505, 3073044997,
    #      1249193625, 1826792401,
    #      1657776532, 5347290193, 1100856704, 1187986757, 1197161814,
    #      1649005320,
    #      1749127163, 1749127163, 1670071920
    # ]
    scrawl_ID = set(start_urls)  # 记录待爬的微博ID
    finish_ID = set()  # 记录已爬的微博ID

    def start_requests(self):
        while True:
            ID = self.scrawl_ID.pop()
            self.finish_ID.add(ID)  # 加入已爬队列
            ID = str(ID)
            follows = []
            followsItems = FollowsItem()
            followsItems["_id"] = ID
            followsItems["follows"] = follows

            fans = []
            fansItems = FansItem()
            fansItems["_id"] = ID
            fansItems["fans"] = fans

            url_follows = "http://weibo.cn/%s/follow" % ID
            url_fans = "http://weibo.cn/%s/fans" % ID
            url_tweets = "http://weibo.cn/%s/profile?filter=0&page=1" % ID
            url_information0 = "http://weibo.cn/attgroup/opening?uid=%s" % ID
            # yield Request(url=url_follows, meta={"item": followsItems, "result": follows},
            #               callback=self.parse3)  # 去爬关注人
            # yield Request(url=url_fans, meta={"item": fansItems, "result": fans}, callback=self.parse3)  # 去爬粉丝

            # yield Request(url=url_information0, meta={"ID": ID}, callback=self.parse0)  # 去爬个人信息
            yield Request(url=url_tweets, meta={"ID": ID}, callback=self.parse2)  # 去爬微博

    def parse0(self, response):
        """ 抓取个人信息1 """
        informationItems = InformationItem()
        selector = Selector(response)
        text0 = selector.xpath('body/div[@class="u"]/div[@class="tip2"]').extract_first()
        if text0:
            num_tweets = re.findall(u'\u5fae\u535a\[(\d+)\]', text0)  # 微博数
            num_follows = re.findall(u'\u5173\u6ce8\[(\d+)\]', text0)  # 关注数
            num_fans = re.findall(u'\u7c89\u4e1d\[(\d+)\]', text0)  # 粉丝数
            if num_tweets:
                informationItems["Num_Tweets"] = int(num_tweets[0])
            if num_follows:
                informationItems["Num_Follows"] = int(num_follows[0])
            if num_fans:
                informationItems["Num_Fans"] = int(num_fans[0])
            informationItems["_id"] = response.meta["ID"]
            url_information1 = "http://weibo.cn/%s/info" % response.meta["ID"]
            yield Request(url=url_information1, meta={"item": informationItems}, callback=self.parse1)

    def parse1(self, response):
        """ 抓取个人信息2 """
        informationItems = response.meta["item"]
        selector = Selector(response)
        text1 = ";".join(selector.xpath('body/div[@class="c"]/text()').extract())  # 获取标签里的所有text()
        ele = selector.xpath('body/div[6]')
        tags = ele.xpath('a/text()').extract()
        tag = ' '.join(tags[:3])
        nickname = re.findall(u'\u6635\u79f0[:|\uff1a](.*?);', text1)  # 昵称
        gender = re.findall(u'\u6027\u522b[:|\uff1a](.*?);', text1)  # 性别
        place = re.findall(u'\u5730\u533a[:|\uff1a](.*?);', text1)  # 地区（包括省份和城市）
        signature = re.findall(u'\u7b80\u4ecb[:|\uff1a](.*?);', text1)  # 个性签名
        Credentials = re.findall(u'认证信息[:|\uff1a](.*?);', text1)
        birthday = re.findall(u'\u751f\u65e5[:|\uff1a](.*?);', text1)  # 生日
        sexorientation = re.findall(u'\u6027\u53d6\u5411[:|\uff1a](.*?);', text1)  # 性取向
        marriage = re.findall(u'\u611f\u60c5\u72b6\u51b5[:|\uff1a](.*?);', text1)  # 婚姻状况
        url = re.findall(u'\u4e92\u8054\u7f51[:|\uff1a](.*?);', text1)  # 首页链接
        if tag:
            informationItems['Tags'] = tag
        if nickname:
            informationItems["NickName"] = nickname[0]
        if gender:
            informationItems["Gender"] = gender[0]
        if place:
            place = place[0].split(" ")
            informationItems["Province"] = place[0]
            if len(place) > 1:
                informationItems["City"] = place[1]
        if Credentials:
            informationItems['Credentials'] = Credentials[0]
        if signature:
            informationItems["Signature"] = signature[0]
        if birthday:
            try:
                birthday = datetime.datetime.strptime(birthday[0], "%Y-%m-%d")
                informationItems["Birthday"] = birthday
            except Exception:
                pass
        if sexorientation:
            if sexorientation[0] == gender[0]:
                informationItems["Sex_Orientation"] = "gay"
            else:
                informationItems["Sex_Orientation"] = "Heterosexual"
        if marriage:
            informationItems["Marriage"] = marriage[0]
        if url:
            informationItems["URL"] = url[0]
        yield informationItems

    def parse2(self, response):
        """ 抓取微博数据 """
        today = datetime.date.today()
        today_str = str(today)
        one_day = datetime.timedelta(days=1)
        year = today_str[0:4]
        selector = Selector(response)
        tweets = selector.xpath('body/div[@class="c" and @id]')
        for tweet in tweets:
            tweetsItems = TweetsItem()
            id = tweet.xpath('@id').extract_first()  # 微博ID
            content_raw = tweet.xpath('div[1]')
            content = content_raw.xpath('string(.)').extract()   # 微博内容 提取标签下所有文本
            content1_raw = tweet.xpath('div[last()]')
            content1 = content1_raw.xpath('string(.)').extract()  # 转发理由
            cooridinates = tweet.xpath('div/a/@href').extract_first()  # 定位坐标

            YoNc = re.findall(u'转发理由', tweet.extract()) #判断是否转发
            like = re.findall(u'\u8d5e\[(\d+)\]', tweet.extract())  # 点赞数
            transfer = re.findall(u'\u8f6c\u53d1\[(\d+)\]', tweet.extract())  # 转载数

            link = content1_raw.xpath('a/@href').extract()
            link_comment = link[-2]  # 评论的链接
            link_repost = link[-3]  # 转发的链接
            # print (link)

            comment = re.findall(u'\u8bc4\u8bba\[(\d+)\]', tweet.extract())  # 评论数
            others = tweet.xpath('div/span[@class="ct"]').xpath('string(.)').extract_first()  # 求时间和使用工具（手机或平台）
            tweetsItems["ID"] = response.meta.get("ID", 'unknown')
            tweetsItems["_id"] = tweetsItems["ID"] + "-" + id
            if YoNc:
                tweetsItems["Content"] = (''.join(content1).strip() + '\n' + u'原文:' + ''.join(content))\
                    .replace(u'&nbsp;', '')
            else:
                tweetsItems["Content"] = (''.join(content)).replace(u'&nbsp;', '')
                    # .strip(u"[\u4f4d\u7f6e]")  # 去掉最后的"[位置]"
            tweetsItems['ColTime'] = datetime.datetime.today()
            if cooridinates:
                cooridinates = re.findall('center=([\d|.|,]+)', cooridinates)
                if cooridinates:
                    tweetsItems["Co_oridinates"] = cooridinates[0]
            if like:
                tweetsItems["Like"] = int(like[-1])
            if transfer:
                tweetsItems["Transfer"] = int(transfer[-1])
            if comment:
                tweetsItems["Comment"] = int(comment[-1])

            if others:
                others = others.split(u"\u6765\u81ea")
                # print(others[0][:2])
                if others[0][:2] == u'今天':
                    others[0] = today_str + others[0][2:]

                elif others[0][1] == u'月' or others[0][2] == u'月':
                    a = others[0].split()
                    b = str(datetime.datetime.strptime(a[0], u'%m月%d日'))[4:10]
                    others[0] = year + b + ' ' + a[1]


                tweetsItems["PubTime"] = others[0]
                # print(tweetsItems['PubTime'])
                if len(others) == 2:
                    tweetsItems["Tools"] = others[1]
            '''计算日期差'''
            if tweetsItems['PubTime'].find(u'前') != -1:
                pass
            else:
                sta_time = datetime.datetime.strptime(tweetsItems['PubTime'][:10], "%Y-%m-%d")
                today1 = datetime.datetime.today()
                days_ago = (today1 - sta_time).days
                if tweetsItems['Content'].find(u'置顶') != -1:
                    pass
                elif days_ago > 3:
                    return
            if link_comment and tweetsItems["Comment"] > 0:
                yield Request(url=link_comment, meta={"ID": tweetsItems['_id'], 'num': 0}, callback=self.parse4)
            if link_repost and tweetsItems['Transfer'] > 0:
                yield Request(url=link_repost, meta={"ID": tweetsItems['_id'], 'num': 0}, callback=self.parse5)
            yield tweetsItems


        url_next = selector.xpath(
            u'body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()
        if url_next:
            yield Request(url=self.host + url_next[0], meta={"ID": response.meta["ID"]}, callback=self.parse2)

    def parse3(self, response):
        """ 抓取关注或粉丝 """
        items = response.meta["item"]
        selector = Selector(response)
        text1 = selector.xpath('body//table/tr/td[2]/a[1]/text()').extract()
        text2 = selector.xpath(
            u'body//table/tr/td/a[text()="\u5173\u6ce8\u4ed6" or text()="\u5173\u6ce8\u5979"]/@href').extract()  #关注他or她
        for a, b in zip(text1, text2):
            b = re.findall('uid=(\d+)', b)
            elem = {}
            elem['id'] = b[0]
            elem['name'] = a
            if elem:
                response.meta['result'].append(elem)

        # for elem in text2:
        #     elem = re.findall('uid=(\d+)', elem)  # uid列表
        #     if elem:
        #         response.meta["result"].append(elem[0])  # result中是uid列表
        #         ID = int(elem[0])
        #         if ID not in self.finish_ID:  # 新的ID，如果未爬则加入待爬队列
        #             self.scrawl_ID.add(ID)
        url_next = selector.xpath(
            u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()
        if url_next:
            yield Request(url=self.host + url_next[0], meta={"item": items, "result": response.meta["result"]},
                          callback=self.parse3)
        else:  # 如果没有下一页即获取完毕
            yield items

    def parse4(self, response):
        today = str(datetime.date.today())
        year = today[0:4]
        selector = Selector(response)
        comments = selector.xpath('body/div[@class="c" and contains(@id,"C_")]')
        num = response.meta.get('num', 'unknown')
        for comment in comments:
            commentItem = CommentItem()
            id = comment.xpath('@id').extract_first()
            name = comment.xpath('a[1]/text()').extract_first()
            homepage = comment.xpath('a[1]/@href').extract_first()
            content = comment.xpath('string(.)').extract()
            like = re.findall(u'\u8d5e\[(\d+)\]', comment.extract())  # 点赞数
            others = comment.xpath('span[@class="ct"]').xpath('string(.)').extract_first()  # 求时间和使用工具（手机或平台）

            commentItem["ID"] = response.meta.get("ID", 'unknown')
            commentItem["_id"] = commentItem["ID"] + "-" + id
            commentItem['Name'] = name
            commentItem['Homepage'] = homepage
            commentItem['Content'] = ''.join(content).replace(u'&nbsp;', '')
            if like:
                commentItem['Like'] = int(like[0])
            if others:
                others = others.split(u"\u6765\u81ea")
                # print(others[0][:2])
                if others[0].find(u'今天') != -1:
                    others[0] = today + others[0][2:]

                elif others[0][1] == u'月' or others[0][2] == u'月':
                    a = others[0].split()
                    try:
                        b = str(datetime.datetime.strptime(year+u'年'+a[0], u'%Y年%m月%d日'))[:10]
                        others[0] = b + ' ' + a[1]
                    except:
                        print(a[0])

                commentItem["PubTime"] = others[0]
                if len(others) == 2:
                    commentItem["Tools"] = others[1]
                yield commentItem
        url_next = selector.xpath(
            u'body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()
        if url_next and num < 20:
            yield Request(url=self.host + url_next[0], meta={"ID": response.meta["ID"], 'num': num+1}, callback=self.parse4)

    def parse5(self, response):
        today = str(datetime.date.today())
        year = today[0:4]
        selector = Selector(response)
        reposts = selector.xpath('body/div[@class="c" and not(@id)]')
        id = response.meta.get('num', 'unknown')
        for repost in reposts:
            if repost.xpath('span'):
                repostItem = RepostItem()
                id = id+1
                name = repost.xpath('a[1]/text()').extract_first()
                homepage = repost.xpath('a[1]/@href').extract_first()
                content = repost.xpath('string(.)').extract()
                like = re.findall(u'\u8d5e\[(\d+)\]', repost.extract())  # 点赞数
                others = repost.xpath('span[@class="ct"]').xpath('string(.)').extract_first()  # 求时间和使用工具（手机或平台）

                repostItem["ID"] = response.meta.get("ID", 'unknown')
                repostItem["_id"] = repostItem["ID"] + "-" + str(id)
                repostItem['Name'] = name
                repostItem['Homepage'] = homepage
                repostItem['Content'] = ''.join(content).replace(u'&nbsp;', '')
                if like:
                    repostItem['Like'] = int(like[0])
                if others:
                    others = others.split(u"\u6765\u81ea")
                    # print(others[0][:2])
                    index = others[0].find(u'今天')
                    if index != -1:
                        others[0] = today + others[0][index+2:]

                    elif others[0][2] == u'月' or others[0][3] == u'月':
                        a = others[0].split()
                        b = str(datetime.datetime.strptime(a[0], u'%m月%d日'))[4:10]
                        others[0] = year + b + ' ' + a[1]

                    repostItem["PubTime"] = others[0]
                    if len(others) == 2:
                        repostItem["Tools"] = others[1]
                    yield repostItem
        url_next = selector.xpath(
            u'body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()
        if url_next and id < 200:
            yield Request(url=self.host + url_next[0], meta={"ID": response.meta["ID"], 'num': id}, callback=self.parse5)

