# author: HuYong
# coding=utf-8
import os
import sys
import urllib
import datetime
import requests
import re
from bs4 import BeautifulSoup

from bdu.model import BDU_Student


class ZhengFangSpider:
    def __init__(self, student, baseUrl):
        reload(sys)
        sys.setdefaultencoding("utf-8")
        self.student = student
        self.baseUrl = baseUrl
        self.session = requests.session()
        self.session.headers[
            'User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'

    # 登陆
    def login(self):
        loginurl = self.baseUrl + "xtgl/login_login.html"
        data = {
            "yhm": student.number,
            "mm": student.password,
        }
        # 登陆教务系统
        loginResponse = self.session.post(loginurl, data=data)
        if loginResponse.status_code == requests.codes.ok:
            print "成功进入教务系统！"
            _t = re.search("&_t=(.*)", loginResponse.url).group(1)
            self.session.headers['Referer'] = self.baseUrl + "xtgl/index_initMenu.html?jsdm=xs&_t=" + _t

    # 获取学生信息
    def getBasicInformation(self):
        url = self.baseUrl + "xsxxxggl/xsgrxxwh_cxXsgrxx.html"
        self.session.headers['Upgrade-Insecure-Requests'] = "1"
        self.session.headers['Origin'] = "http://jwgl.bdu.edu.cn"
        data = {
            "gnmkdm": "N100801",
            "dyym": "/xsxxxggl/xsgrxxwh_cxXsgrxx.html",
            "gnmkmc": "%E6%9F%A5%E8%AF%A2%E4%B8%AA%E4%BA%BA%E4%BF%A1%E6%81%AF",  # 查询个人信息
            "sessionUserKey": student.number,
            "sfgnym":"",
            "layout":"func-layout",
            "gnmkdmKey":"index",
        }
        response = self.session.post(url, data=data)
        #print response.content
        soup = BeautifulSoup(response.content,"html5lib")
        basicDiv = soup.find("div",class_="col-md-8 col-sm-8")
        infors = basicDiv.find_all("p",class_="form-control-static")
        print "\n*********开始获取个人信息*********\n"
        for infor in infors:
            print infor.string.strip()


if __name__ == "__main__":
    student = BDU_Student("**换成学号****", "***换成密码*****")
    spider = ZhengFangSpider(student, baseUrl="http://jwgl.bdu.edu.cn/")  # 实例化爬虫
    spider.login()
    spider.getBasicInformation()
