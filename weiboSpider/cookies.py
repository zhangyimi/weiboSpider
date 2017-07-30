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
    {'no': '15127116246', 'psw': 'q123123'}, {'no': '14763031165', 'psw': 'q123123'},
    {'no': '14763031065', 'psw': 'q123123'}, {'no': '14763029652', 'psw': 'q123123'},
    {'no': '13270451296', 'psw': 'q123123'}, {'no': '13314959614', 'psw': 'q123123'},
    {'no': '13105492349', 'psw': 'q123123'}, {'no': '14763047561', 'psw': 'q123123'},
    {'no': '14763047523', 'psw': 'q123123'}, {'no': '13181491334', 'psw': 'q123123'},
    {'no': '13165397429', 'psw': 'q123123'}, {'no': '15853458485', 'psw': 'q123123'},
    {'no': '13026348308', 'psw': 'q123123'},
    {'no': '13335181414', 'psw': 'q123123'}, {'no': '13473117812', 'psw': 'q123123'},
    {'no': '13335165149', 'psw': 'q123123'}, {'no': '13335183479', 'psw': 'q123123'},
    {'no': '13335174196', 'psw': 'q123123'}, {'no': '18937621490', 'psw': 'q123123'},
    {'no': '18134744248', 'psw': 'q123123'}, {'no': '13189846543', 'psw': 'q123123'},
    {'no': '15503622050', 'psw': 'q123123'}, {'no': '13250412342', 'psw': 'q123123'},
    {'no': '15581825220', 'psw': 'q123123'}, {'no': '13229548646', 'psw': 'q123123'},
    {'no': '18039086664', 'psw': 'q123123'}, {'no': '13087964550', 'psw': 'q123123'},
    {'no': '18039087247', 'psw': 'q123123'}, {'no': '18039087406', 'psw': 'q123123'},
    {'no': '17307678936', 'psw': 'q123123'}, {'no': '18174801049', 'psw': 'q123123'},
    {'no': '13335162436', 'psw': 'q123123'}, {'no': '13335172419', 'psw': 'q123123'},
    {'no': '13323849060', 'psw': 'q123123'}, {'no': '17702658001', 'psw': 'q123123'},
    {'no': '15053031844', 'psw': 'q123123'}, {'no': '17737140656', 'psw': 'q123123'},
    {'no': '17307678903', 'psw': 'q123123'}, {'no': '17303045100', 'psw': 'q123123'},
    {'no': '17307678972', 'psw': 'q123123'}, {'no': '17303045115', 'psw': 'q123123'},
    {'no': '17307678879', 'psw': 'q123123'}, {'no': '14523533737', 'psw': 'q123123'},
    {'no': '13229543045', 'psw': 'q123123'}, {'no': '13124925314', 'psw': 'q123123'},
    {'no': '13250408947', 'psw': 'q123123'}, {'no': '15360373582', 'psw': 'q123123'},
    {'no': '15678961095', 'psw': 'q123123'}, {'no': '18315914334', 'psw': 'q123123'},
    {'no': '14523528953', 'psw': 'q123123'}, {'no': '13074151488', 'psw': 'q123123'},
    {'no': '13236949490', 'psw': 'q123123'}, {'no': '15942322481', 'psw': 'q123123'},
    {'no': '15942322430', 'psw': 'q123123'}, {'no': '15942322891', 'psw': 'q123123'},
    {'no': '18240337457', 'psw': 'q123123'}, {'no': '15710565982', 'psw': 'q123123'},
    {'no': '13335168406', 'psw': 'q123123'}, {'no': '18665729641', 'psw': 'q123123'},
    {'no': '13074199419', 'psw': 'q123123'}, {'no': '13276552894', 'psw': 'q123123'},
    {'no': '13250411645', 'psw': 'q123123'}, {'no': '18039087419', 'psw': 'q123123'},
    {'no': '18039087614', 'psw': 'q123123'}, {'no': '13192048793', 'psw': 'q123123'},
    {'no': '17099398041', 'psw': 'q123123'}, {'no': '13202055710', 'psw': 'q123123'},
    {'no': '13266429045', 'psw': 'q123123'}, {'no': '13245868497', 'psw': 'q123123'},
    {'no': '13245884671', 'psw': 'q123123'}, {'no': '18240118726', 'psw': 'q123123'},
    {'no': '18240118952', 'psw': 'q123123'}, {'no': '13265290587', 'psw': 'q123123'},
    {'no': '18039087584', 'psw': 'q123123'}, {'no': '18039087454', 'psw': 'q123123'},
    {'no': '18039087453', 'psw': 'q123123'}, {'no': '18039087464', 'psw': 'q123123'},
    {'no': '18673506825', 'psw': 'q123123'}, {'no': '18692774869', 'psw': 'q123123'},
    {'no': '18692776401', 'psw': 'q123123'}, {'no': '18573158144', 'psw': 'q123123'},
    {'no': '18670260283', 'psw': 'q123123'}, {'no': '18673504692', 'psw': 'q123123'},
    {'no': '18573168240', 'psw': 'q123123'}, {'no': '15710594886', 'psw': 'q123123'},
    {'no': '17081622467', 'psw': 'q123123'}, {'no': '15710594928', 'psw': 'q123123'},
    {'no': '15710595747', 'psw': 'q123123'}, {'no': '13246534742', 'psw': 'q123123'},
    {'no': '15710594926', 'psw': 'q123123'}, {'no': '17012746332', 'psw': 'q123123'},
    {'no': '17012746950', 'psw': 'q123123'}, {'no': '18039087642', 'psw': 'q123123'},
    {'no': '13250418846', 'psw': 'q123123'}, {'no': '13266422343', 'psw': 'q123123'},
    {'no': '17079501194', 'psw': 'q123123'}, {'no': '14523531831', 'psw': 'q123123'},
    {'no': '17087902334', 'psw': 'q123123'}, {'no': '15710595883', 'psw': 'q123123'},
    {'no': '13078242646', 'psw': 'q123123'}, {'no': '14740488988', 'psw': 'q123123'},
    {'no': '17303042525', 'psw': 'q123123'}, {'no': '13250418242', 'psw': 'q123123'}, ]


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
