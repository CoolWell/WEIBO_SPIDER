# encoding=utf-8
import pymongo
from items import InformationItem, TweetsItem, FollowsItem, FansItem, CommentItem, RepostItem
import datetime

class MongoDBPipleline(object):
    def __init__(self):
        today = str(datetime.date.today())
        addresses = ['223.3.77.26:20000', '223.3.83.196:20000', '223.3.90.150:20000']
        clinet = pymongo.MongoClient(addresses)

        # clinet = pymongo.MongoClient("223.3.77.26", 20000)
        db = clinet["Sina_test"]
        self.Information = db["Information-"+today]
        self.Tweets = db["Tweets-"+today]
        self.Follows = db["Follows-"+today]
        self.Fans = db["Fans-"+today]

        self.Comment = db['Comment-'+today]
        self.Repost = db['Repost-'+today]

    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        if isinstance(item, InformationItem):
            try:
                self.Information.insert(dict(item))
            except Exception:
                pass
        elif isinstance(item, CommentItem):
            try:
                self.Comment.insert(dict(item))
            except Exception:
                pass
        elif isinstance(item, RepostItem):
            try:
                self.Repost.insert(dict(item))
            except Exception:
                pass
        elif isinstance(item, TweetsItem):
            try:
                self.Tweets.insert(dict(item))
            except Exception:
                pass
        elif isinstance(item, FollowsItem):
            followsItems = dict(item)
            # follows = followsItems.pop("follows")
            # for i in range(len(follows)):
            #     followsItems[str(i + 1)] = follows[i]
            try:
                self.Follows.insert(followsItems)
            except Exception:
                pass
        elif isinstance(item, FansItem):
            fansItems = dict(item)
            # fans = fansItems.pop("fans")
            # for i in range(len(fans)):
            #     fansItems[str(i + 1)] = fans[i]
            try:
                self.Fans.insert(fansItems)
            except Exception:
                pass

        return item
