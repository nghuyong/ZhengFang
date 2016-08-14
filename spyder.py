# author: HuYong
# coding=utf-8
import os
import sys
import urllib
import datetime
import requests
from lxml import etree
from ZhengFang.parseHtml import  getClassScheduleFromHtml, getStudentInfor
from ZhengFang.model import Student, db, ClassSchedule, Class


class ZhengFangSpyder:

    def __init__(self,student,baseUrl="http://202.195.144.168/jndx"):
        reload(sys)
        sys.setdefaultencoding("utf-8")
        self.student = student
        self.baseUrl = baseUrl
        self.session = requests.session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'


    def login(self):
        loginurl = self.baseUrl+"/default2.aspx"
        response = self.session.get(loginurl)
        selector = etree.HTML(response.content)
        __VIEWSTATE = selector.xpath('//*[@id="form1"]/input/@value')[0]
        imgUrl = self.baseUrl+"/CheckCode.aspx?"
        imgresponse = self.session.get(imgUrl, stream=True)
        image = imgresponse.content
        DstDir = os.getcwd() + "\\"
        print("保存验证码到：" + DstDir + "code.jpg" + "\n")
        try:
            with open(DstDir + "code.jpg", "wb") as jpg:
                jpg.write(image)
        except IOError:
            print("IO Error\n")
        finally:
            jpg.close
        code = raw_input("验证码是：")
        RadioButtonList1 = u"学生".encode('gb2312', 'replace')
        data = {
            "RadioButtonList1": RadioButtonList1,
            "__VIEWSTATE": __VIEWSTATE,
            "TextBox1": self.student.studentnumber,
            "TextBox2": self.student.password,
            "TextBox3": code,
            "Button1": "",
            "lbLanguage": ""
        }
        # 登陆教务系统
        Loginresponse = self.session.post(loginurl, data=data)
        if Loginresponse.status_code == requests.codes.ok:
            print "成功进入教务系统！"


    def loginWithOutCode(self):
        loginurl = self.baseUrl + "/default5.aspx"
        response = self.session.get(loginurl)
        selector = etree.HTML(response.content)
        __VIEWSTATE = selector.xpath('//*[@id="form1"]/input/@value')[0]
        RadioButtonList1 = u"学生".encode('gb2312', 'replace')
        data = {
            "RadioButtonList1": RadioButtonList1,
            "__VIEWSTATE": __VIEWSTATE,
            "TextBox1": self.student.studentnumber,
            "TextBox2": self.student.password,
            "Button1": "",
        }
        # 登陆教务系统
        Loginresponse = self.session.post(loginurl, data=data)
        if Loginresponse.status_code == requests.codes.ok:
            print "成功进入教务系统！"



    def getStudentBaseInfo(self):
        self.session.headers['Referer'] = self.baseUrl+"/xs_main.aspx?xh="+self.student.studentnumber
        url = self.baseUrl+"/xsgrxx.aspx?xh="+self.student.studentnumber+"&"
        response = self.session.get(url)
        d = getStudentInfor(response)
        self.student.idCardNumber =d["idCardNumber"]
        self.student.name =d["name"]
        self.student.urlName = urllib.quote_plus(str(d["name"].encode('gb2312')))
        self.student.sex =d["sex"]
        self.student.enterSchoolTime =d["enterSchoolTime"]
        self.student.birthsday =d["birthsday"]
        self.student.highschool =d["highschool"]
        self.student.nationality =d["nationality"]
        self.student.hometown =d["hometown"]
        self.student.politicsStatus =d["politicsStatus"]
        self.student.college =d["college"]
        self.student.major =d["major"]
        self.student.classname =d["classname"]
        self.student.gradeClass =d["gradeClass"]
        self.student.save()
        print "读取学生基本信息成功"

    
    def getClassSchedule(self):
        url = self.baseUrl+"/xskbcx.aspx?xh=" + self.student.studentnumber + "&xm=" + self.student.urlName + "&gnmkdm=N121603"
        response = self.session.get(url, allow_redirects=False)
        __VIEWSTATE = getClassScheduleFromHtml(response)["__VIEWSTATE"]
        year = int(self.student.gradeClass)
        term = 1
        today = datetime.date.today()
        while today.year>year or (today.year==year and today.month>=7 and term==1):
            data = {
                "__EVENTTARGET": "xqd",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": __VIEWSTATE,
                "xnd": str(year)+"-"+str(year+1),
                "xqd": str(term),
            }
            self.session.headers['Referer'] = url
            response = self.session.post(url,data)
            print "正在获取"+str(year)+"-"+str(year+1)+"学年第"+str(term)+"学期课表"
            classes = getClassScheduleFromHtml(response)["classes"]
            __VIEWSTATE = getClassScheduleFromHtml(response)["__VIEWSTATE"]
            classSchedule = ClassSchedule(student=self.student,year=str(year)+"-"+str(year+1),term=term)
            classSchedule.save()
            for each in classes:
                oneClass = Class(schedule = classSchedule , name = each["name"] , type = each["type"] ,
                                 timeInTheWeek = each["timeInTheWeek"],timeInTheDay = each["timeInTheDay"] , timeInTheTerm = each["timeInTheTerm"],
                                 teacher = each["teacher"] , location = each["location"]
                                 )
                oneClass.save()
            term = term + 1
            if term>2:
                term = 1
                year = year+1
        print "成功获取课表"






if __name__ == "__main__":
    try:
        db.connect()
        db.create_tables([Student, ClassSchedule,Class])
    except Exception ,e:
        print e
    student = Student(studentnumber="1030614418",password="342626199509064718") #换成自己的，不要用我的账号测试！！
    student.save()
    spyder = ZhengFangSpyder(student)
    spyder.loginWithOutCode()
    spyder.getStudentBaseInfo()
    spyder.getClassSchedule()

