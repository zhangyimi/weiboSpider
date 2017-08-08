#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from selenium import webdriver
import logging
from weiboSpider.login import getType, draw
from multiprocessing.dummy import Pool
import json

logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.WARNING)  # 将selenium的日志级别设成WARNING，太烦人

"""
输入你的微博账号和密码，可去淘宝买。
建议买几十个，微博限制的严，太频繁了会出现302转移。
或者你也可以把时间间隔调大点。
"""
myWeiBo = [
    {'no': '15127116246', 'psw': 'q123123'},
   ]


def getCookies(weibo):
    """ 获取Cookies """

    account = weibo['no']
    password = weibo['psw']
    try:
        browser = webdriver.Chrome()
        browser.set_window_size(1050, 840)
        browser.get('https://passport.weibo.cn/signin/login?entry=mweibo&r=https://weibo.cn/')

        time.sleep(1)
        name = browser.find_element_by_id('loginName')
        psw = browser.find_element_by_id('loginPassword')
        login = browser.find_element_by_id('loginAction')
        name.send_keys(account)  # 测试账号
        psw.send_keys(password)
        login.click()
        try:
            ttype = getType(browser)  # 识别图形路径
            print('Result: %s!' % ttype)
            draw(browser, ttype)  # 滑动破解

        except:
            pass

        time.sleep(4)
        cookie = {}
        if "我的首页" in browser.title:
            for elem in browser.get_cookies():
                cookie[elem["name"]] = elem["value"]

            if len(cookie) > 0:
                logger.warning("Get Cookie Successful: %s" % account)



    except Exception as e:
        logger.warning("Failed %s!" % account)
        logger.warning("cookies is %s" % browser.get_cookies())
    finally:
        try:
            browser.close()
        except Exception as e:
            pass
    return cookie


pool = Pool()
cookies = pool.map(getCookies, myWeiBo)
logger.warning("Get Cookies Finish!( Num:%d)" % len(cookies))
