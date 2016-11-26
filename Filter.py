# -*- coding: utf-8 -*-
__author__ = 'Passion'
import pymongo


clinet = pymongo.MongoClient("localhost", 27017)
db = clinet["Sina"]
def handle():
    name='Information-2016-10-27'
    source = db[name]
    intention = db['weibo_id']
    for item in source.find():
       if item['Num_Fans'] > 10000 and dict(item).get('Credentials'):
           intention.insert(item)


def sort():
    source = db['weibo_id']
    intention = db['weibo_id_after']
    for item in source.find().sort('Num_Fans', -1):
        intention.insert(item)

def out():
    source = db['weibo_id_after']
    f = open(r'C:\weibo.txt', 'a')
    for i, item in enumerate(source.find()):
        if i == 20000:
            break
        f.write(item['_id']+'\n')
    f.close()





if __name__ == "__main__":
    # handle()
    # sort()
    out()
