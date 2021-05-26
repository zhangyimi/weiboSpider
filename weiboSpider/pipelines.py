# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html




import pymongo
from weiboSpider.items import InformationItem,TweetsItem
import pymysql

import logging
logger = logging.getLogger(__name__)
class WeibospiderPipeline(object):
    def __init__(self):
        self.count = 1
        self.conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            # 这里填写密码
            passwd='',
            db='weibo',
            charset='utf8',
        )
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """

        if isinstance(item, TweetsItem):
            try:
                print("***********at beginning of saving**********")

                sql = ''
                sql += str(
                    'INSERT INTO weibo.TweetsItem (`WId`,`UId`,`WContent`,`PubTime`,`Tools`,`Like`,`Comment`,`Transfer`) ')
                sql += str(' Values(\'')
                sql += str(item['WId']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['UId']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['WContent']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['PubTime']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['Tools']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['Like']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['Comment']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['Transfer']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\')')


                self.cur.execute(sql)
                self.conn.commit()
                self.count = self.count + 1

            except Exception as e:
                self.conn.rollback()
                logger.error("插入微博失败，原因：{}".format(e))


        elif isinstance(item, InformationItem):
            try:
                print("***********at beginning of saving**********")

                sql = ''
                sql += str(
                    'INSERT INTO weibo.informationitem (`UId`,`NickName`,`Gender`,`Province`,`City`,`BriefIntroduction`,`Tag`,`Birthday`,`Num_Tweets`,`Num_Follows`,`Num_Fans`,`VIPlevel`,`Authentication`,`AuthenticationInformation`,`url`) ')
                sql += str(' Values(\'')
                sql += str(item['UId']).encode("gbk",'ignore').decode("gbk",'ignore')

                sql += str('\', \'')
                sql += str(item['NickName']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['Gender']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['Province']).encode("gbk",'ignore').decode("gbk",'ignore')

                sql += str('\', \'')
                sql += str(item['City']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['BriefIntroduction']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')

                sql += str(item['Tag']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['Birthday']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['Num_Tweets']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['Num_Follows']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['Num_Fans']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['VIPlevel']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['Authentication']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['AuthenticationInformation']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\', \'')
                sql += str(item['URL']).encode("gbk",'ignore').decode("gbk",'ignore')
                sql += str('\')')



                self.cur.execute(sql)
                self.conn.commit()

                self.count = self.count + 1
                print(self.count)
            except Exception as e:
                self.conn.rollback()

                logger.error("插入用户失败，原因：{}".format(e))



            ##在Java开发中，Dao连接会对内存溢出，需要定时断开重连，这里不清楚是否需要，先加上了
            if self.count == 1000:
                print("try reconnecting")
                self.count = 0
                self.cur.close()
                self.conn.close()
                self.conn = pymysql.connect(
                    host='localhost',
                    port=3306,
                    user='root',
                    passwd='xxx',
                    db='weibo',
                    charset='utf8',
                )
                self.cur = self.conn.cursor()
                print("reconnect")

        return item


