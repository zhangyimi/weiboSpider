# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from weiboSpider.GetIp import GetIp
from weiboSpider.user_agents import agents
# from weiboSpider.cookies import cookies
import scrapy.downloadermiddlewares.retry
from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError
import pickle
import redis
import requests
import random
import time
import logging

pool = redis.ConnectionPool(host="127.0.0.1", port="6379")
r = redis.Redis(connection_pool=pool)
logger = logging.getLogger("request")


# r.sadd("cookie",*cookies)
# 获得cookie，每次第一次运行时启动一遍就好。

class ProxyMiddleware():
    # overwrite process request
    def process_request(self, request, spider):
        # Set the location of the proxy


        retries = request.meta.get('retry_times', 0)

        if retries :
            logger.debug("retries is {}".format(retries))
            try:

                now_proxy = request.meta["proxy"].split("//")[1]
                logger.debug("proxy {} is error".format(now_proxy))
                invaild_proxy = now_proxy
                r.srem("proxy", invaild_proxy)
            except Exception as e:
                logger.error("Exception is {}".format(e))
                logger.error("request.meta['proxy'] is {}".format(request.meta["proxy"]))
            proxy =r.srandmember("proxy")
            if proxy:
                proxy = "https://" + proxy.decode("utf-8")
                request.meta["proxy"] = proxy
                logger.debug("because some exception,fail {} time, delete the proxy {}".format(retries, invaild_proxy))
                logger.debug("get a new proxy is {}".format(proxy))

            if r.scard("proxy") < 15:
                self.get_proxy()

        else:

            request.meta["dont_redirect"] = True
            if  r.scard("proxy") <15:
                self.get_proxy()
            proxy = r.srandmember("proxy")
            if proxy:

                proxy = "https://" + proxy.decode("utf-8")
                request.meta["proxy"] = proxy



    def process_response(self, response, request, spider):
        if response.status not in [300, 301, 302, 303, ] and not ( 200<=response.status<300):
            proxy =  "https://" + r.srandmember("proxy").decode("utf-8")
            request.meta["proxy"] = proxy
            return request

        return response





    def get_proxy(self):
        time.sleep(random.randint(2,5))
        url_response = requests.get(
            url="http://vtp.daxiangdaili.com/ip/?tid=558440422474841&filter=on&num=20&protocol=https&sortby=time&delay=15&longlife=10")
        urls = url_response.text
        if not ("ERROR"  or "没有找到" or "<") in urls :
            urls =urls.split("\r")
            urls = [i.replace("\r\n", "").replace("\n", "").replace("\r", "") for i in urls]

            r.sadd("proxy", *urls)
        else:
            logger.debug("get error url:{}".format(urls))
            logger.debug("don't get proxy,please wait 100s")
            time.sleep(100)


class UserAgentMiddleware():
    """ 换User-Agent """

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent


class CookiesMiddleware():
    """ 换Cookie """

    def process_request(self, request, spider):
        cookie = r.srandmember("cookie").decode()
        request.cookies = eval(cookie)

    def process_response(self, response, request, spider):
        if response.status in [300, 301, 302, 303, ]:
            r.srem("cookie", request.cookies)
            logging.debug("because the statuscode {},所以删除cookie".format(response.status))

        return response
