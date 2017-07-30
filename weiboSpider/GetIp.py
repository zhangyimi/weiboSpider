#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' a test module '

__author__ = 'Zhang Shuai'
import pymysql
import time
import requests
from multiprocessing.dummy import Pool

dbapi = "MySQLdb"
kwargs = {'user': 'root',
          'passwd': 'zxc5667456m',
          'db': 'test',
          'host': 'localhost',
          'use_unicode': True}



class GetIp():
    def __init__(self):
        sql = '''SELECT IP,PORT,TYPE FROM proxy WHERE   SPEED<5  and type = "HTTPS"
 ORDER BY proxy.SPEED ASC LIMIT 300
		'''
        con = pymysql.connect(**kwargs)
        cur = con.cursor()
        try:

            cur.execute(sql)
            self.result = cur.fetchall()

        except Exception as e:
            print("select error:", e)
            con.rollback()
        else:
            con.commit()
        cur.close()
        con.close()

    def del_ip(self, record):
        sql = "delete from proxy where IP=%s"
        print(sql)
        con = pymysql.connect(**kwargs)
        cur = con.cursor()
        try:
            print("要删除的ip是：", record[0])
            cur.execute(sql, (record[0],))
        except Exception as e:
            print("delete error:", e)
            con.rollback()
        else:
            con.commit()
        cur.close()
        con.close()
        print(record, " was delete")

    def judge_ip(self, record):
        proxy_type = record[2].lower()
        url = "https://www.baidu.com/"
        proxy = "%s:%s" % (record[0], record[1])
        try:
            proxies = {}
            proxies[proxy_type] = proxy_type + r"://" + proxy
            print(proxy_type, proxies)

            response = requests.get(url, proxies=proxies, timeout=3)

        except Exception  as e:
            print("Requst Error:", e)
            self.del_ip(record)
            return False
        else:
            code = response.status_code

            print("返回的code：", code)
            if int(code) >= 200 and int(code) < 300:

                print('\033[1;33;44mEffective proxy:{}\033[0m'.format( proxies[proxy_type]))
                print("success code :", code)
                return  proxies[proxy_type]
            else:
                print("Invalide proxy", record)
                self.del_ip(record)
                return False

    def get_ips(self):
        print("Proxy getip was execute.")
        pool = Pool()
        result = pool.map(self.judge_ip,self.result)
        pool.close()
        pool.join()
        result =[ i for i in result if i]
        print("共获得可用ip{}个".format(len(result)))
        return result




