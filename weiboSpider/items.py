# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field



class InformationItem(Item):
    """ 个人信息 """
    UId = Field()  # 用户ID
    NickName = Field()  # 昵称
    Gender = Field()  # 性别
    Province = Field()  # 所在省
    City = Field()  # 所在城市
    BriefIntroduction = Field()  # 简介
    Tag = Field() #标签
    Birthday = Field()  # 生日
    Num_Tweets = Field()  # 微博数
    Num_Follows = Field()  # 关注数
    Num_Fans = Field()  # 粉丝数
    VIPlevel = Field()  # 会员等级
    Authentication = Field()  # 认证
    AuthenticationInformation = Field() #认证信息
    URL = Field()  # 首页链接


class TweetsItem(Item):
    """ 微博信息 """
    WId = Field()  # 用户ID
    UId = Field()  # 用户ID
    WContent = Field()  # 微博内容
    PubTime = Field()  # 发表时间

    Tools = Field()  # 发表工具/平台
    Like = Field()  # 点赞数
    Comment = Field()  # 评论数
    Transfer = Field()  # 转载数



