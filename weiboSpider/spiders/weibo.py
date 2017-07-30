# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy import Request
import datetime
from scrapy.spiders import CrawlSpider, Rule
import redis
import logging
from lxml import html
from weiboSpider.items import InformationItem, TweetsItem
import regex as re
import requests
import os
import scrapy.spidermiddlewares.httperror


class WeiboSpider(CrawlSpider):
    logging.basicConfig(filename=os.path.join(os.getcwd(), 'log.txt'), level = logging.WARN, filemode = 'a', format = '%(asctime)s - %(levelname)s: %(message)s')
    logging.getLogger("weibo.spider").setLevel(logging.WARNING)

    name = 'weibo'
    allowed_domains = ['weibo.cn']

    pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
    r = redis.Redis(connection_pool=pool)
    # r.delete("had_find_time")
    r.delete("to_find_time")
    r.delete("proxy")
    # r.delete("userid")
    nowTime = datetime.datetime.now()
    days = 0
    while days < 365:
        time = (nowTime - datetime.timedelta(days=days)).strftime("%Y%m%d")
        days += 1
        r.sadd("to_find_time", time)

    def start_requests(self):
        to_find = self.r.spop("to_find_time")

        while to_find:
            to_find = datetime.datetime.strptime(to_find.decode(), "%Y%m%d")

            post_time = to_find.strftime("%Y%m%d")
            pre_time = (to_find - datetime.timedelta(days=1)).strftime("%Y%m%d")

            if not self.r.sismember("had_find_time", post_time):
                logging.debug("{}-{} is finding time".format(pre_time, post_time))

                url = "https://weibo.cn/search/mblog?hideSearchFrame=&keyword=王者荣耀&advancedfilter=1&starttime=" + pre_time + "&endtime=" + post_time + "&sort=hot&page=7"

                yield Request(url=url, callback=self.parse,meta={"post_time":post_time}, dont_filter=True)
            else:
                logging.debug("{}-{} have found ".format(pre_time, post_time))
            to_find = self.r.spop("to_find_time")


    def parse(self, response):
        post_time = response.meta["post_time"]

        tweetsItem = TweetsItem()
        contents = response.xpath("/html/body/div[@id and @class='c']")
        page_url = ""

        for content in contents:
            wid = content.xpath(".//@id").extract()[0]
            if not self.r.sismember("wid", wid):
                url = content.xpath(".//a[@class='nk']/@href").extract()[0]
                find = content.extract()
                like = re.findall("(?<=赞\[)\d*(?=\]</a>)", find)[0]
                comment = re.findall("(?<=评论\[)\d*(?=\]</a>)", find)[0]
                transfer = re.findall("(?<=转发\[)\d*(?=\]</a>)", find)[0]

                uid = re.findall("(?<=/)[^/]*$", url)[0]
                try:
                    int(uid)
                except:
                    uid = re.findall('(?<=uid=)\d*(?=&amp;rl=1">转发)', find)[0]

                wcontent = " ".join(content.xpath(".//span[@class='ctt']").extract())
                wcontent = re.sub("<[a|span|br|]{1}.*?>","",wcontent)
                wcontent = re.sub("</.*?>","",wcontent).replace(r"\u200b","")

                pubtimeAndtool = " ".join(content.xpath(".//span[@class='ct']/text()").extract())

                pubtime, tool = self.get_timeAndtool(pubtimeAndtool)

                tweetsItem["WId"] = wid
                tweetsItem["UId"] = uid
                tweetsItem["WContent"] = wcontent
                tweetsItem["PubTime"] = pubtime

                tweetsItem["Tools"] = tool
                tweetsItem["Like"] = like
                tweetsItem["Comment"] = comment
                tweetsItem["Transfer"] = transfer

                yield tweetsItem
                self.r.sadd("wid", wid)
                if not self.r.sismember("userid", uid):
                    yield Request(url="https://weibo.cn/" + uid + "/info", callback=self.parse_ziliao)
                    self.r.sadd("userid", uid)
            page_list = response.xpath("/html/body/div[@id='pagelist']/form/div/a")
            for i in page_list:
                if "下页" in i.xpath("./text()").extract()[0]:
                    page_url = "https://weibo.cn" + i.xpath("./@href").extract()[0]
        if page_url:
            yield Request(url=page_url, callback=self.parse,meta={"post_time":post_time},dont_filter=True)
        else:
            self.r.sadd("had_find_time", post_time)
            logging.debug("post_time {} add in to_find_time".format(post_time))

    def parse_ziliao(self, response):
        informationItem = InformationItem()
        contents = response.xpath("/html/body/div[@class='c']")
        UId = re.findall("(?<=weibo.cn/).*?(?=/info)", response.url)[0]
        for content in contents:
            content = content.extract()

            if "会员等级" in content:
                if "未开通" in content:
                    informationItem["VIPlevel"] = "未开通"
                else:
                    VIPlevel = re.findall("(?<=会员等级：)\d*级", content)
                    if VIPlevel:
                        informationItem["VIPlevel"] = VIPlevel[0]
            if "昵称" in content and "性别" in content:

                NickName = re.findall("(?<=昵称:).*?(?=<br>)", content)
                Gender = re.findall("(?<=性别:).*?(?=<br>)", content)
                Birthday = re.findall("(?<=生日:).*?(?=<br>)", content)
                BriefIntroduction = re.findall("(?<=简介:).*?(?=<br>)", content)
                Authentication = re.findall("(?<=认证:).*?(?=<br>)", content)
                AuthenticationInformation = re.findall("(?<=认证信息：).*?(?=<br>)", content)
                area = re.findall("(?<=地区:).*?(?=<br>)", content)
                City, Province = "", ""

                URL = "https://weibo.cn/u/" + UId
                informationItem["Tag"] = ""
                if "标签" in content:
                    Tag_url = re.findall('[^<]*(?=">更多)', content)
                    if Tag_url:
                        Tag_url = "https://weibo.cn" + re.findall('(?<=href=").*', Tag_url[0])[0].replace("amp;", "")

                        try:

                            proxy = "https://" + self.r.srandmember("proxy").decode("utf-8")

                            ptype = "https" if "https" in proxy else "http"
                            Tag_respnse = requests.get(url=Tag_url, cookies=response.request.cookies, timeout=20,
                                                       proxies={ptype: proxy})
                            Tag_html = re.findall("<html.*", Tag_respnse.text)[0]
                            Tag_html = html.fromstring(Tag_html)
                            Tag_contents = Tag_html.xpath("/html/body/div[@class='c']")
                            for Tag_content in Tag_contents:
                                if "的标签:" in Tag_content.xpath("./text()")[0]:
                                    Tag = " ".join(Tag_content.xpath("./a/text()"))
                                    informationItem["Tag"] = Tag
                        except Exception as e:
                            informationItem["Tag"] = ""
                            logging.debug('Exception is {}'.format(e))
                if area:
                    area = area[0].strip().split(" ")
                    if len(area) == 2:
                        Province, City = area
                    else:
                        Province = City = area[0]
                informationItem["UId"] = UId
                informationItem["URL"] = URL

                if NickName:
                    informationItem["NickName"] = NickName[0]
                else:
                    informationItem["NickName"] = " "

                if Gender:
                    informationItem["Gender"] = Gender[0]
                else:
                    informationItem["Gender"] = " "
                if Birthday:
                    informationItem["Birthday"] = Birthday[0]
                else:
                    informationItem["Birthday"] = " "
                if BriefIntroduction:
                    informationItem["BriefIntroduction"] = BriefIntroduction[0]
                else:
                    informationItem["BriefIntroduction"] = " "
                if Authentication:
                    informationItem["Authentication"] = Authentication[0]
                else:
                    informationItem["Authentication"] = " "
                if AuthenticationInformation:
                    informationItem["AuthenticationInformation"] = AuthenticationInformation[0]
                else:
                    informationItem["AuthenticationInformation"] = " "
                if Province:
                    informationItem["Province"] = Province
                else:
                    informationItem["Province"] = " "
                if City:
                    informationItem["City"] = City
                else:
                    informationItem["City"] = " "
                yield Request(url="https://weibo.cn/" + UId, meta={"informationItem": informationItem},
                              callback=self.parse_shouye)
                break

    def parse_shouye(self, response):
        nums = " ".join(response.xpath("//div[@class='tip2']/a/text()").extract())
        Num_Tweets = response.xpath("//span[@class ='tc']/text()").extract()[0]
        Num_Tweets = re.search("微博\[(\d*)\]", Num_Tweets).group(1)
        Num_Follows = re.search("关注\[(\d*)\]", nums).group(1)
        Num_Fans = re.search("粉丝\[(\d*)\]", nums).group(1)
        informationItem = response.meta["informationItem"]
        informationItem["Num_Tweets"] = Num_Tweets
        informationItem["Num_Follows"] = Num_Follows
        informationItem["Num_Fans"] = Num_Fans
        yield informationItem

    def get_timeAndtool(self, timeAndtool):
        now_time = datetime.datetime.now()
        pubtime = ""
        tool = ""
        if "分钟" in timeAndtool:
            minute = re.findall("\d*?(?=分钟)", timeAndtool)
            if len(minute):
                pubtime = now_time - datetime.timedelta(minutes=int(minute[0]))
            pubtime = pubtime.strftime("%Y-%m-%d %H:%M")
        elif "今天" in timeAndtool:

            hour, minute = re.findall("(?<=今天 )\d{2}:\d{2}", timeAndtool)[0].split(":")
            if hour and minute:
                pubtime = now_time.strftime("%Y-%m-%d") + " " + hour + ":" + minute
        elif "月" in timeAndtool and "日" in timeAndtool:
            time = re.findall("\d{2}月\d{2}日 \d{2}:\d{2}", timeAndtool)
            if len(time):
                pubtime = datetime.datetime.strptime("2017 " + time[0], "%Y %m月%d日 %H:%M").strftime("%Y-%m-%d %H:%M")

        elif len(re.findall("\d{4}-\d{2}-\d{2} \d{2}:\d{2}", timeAndtool)):
            pubtime = re.findall("\d{4}-\d{2}-\d{2} \d{2}:\d{2}", timeAndtool)[0]
        if "来自" in timeAndtool:
            tool = re.findall("(?<=来自).*", timeAndtool)
            if len(tool):
                tool = tool[0]
        return pubtime, tool
