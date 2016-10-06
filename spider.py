# author: HuYong
# coding=utf-8
import os
import sys
import urllib
import datetime
import requests
from lxml import etree
from ZhengFang.parseHtml import  getClassScheduleFromHtml, getStudentInfor, get__VIEWSTATE, getGrade
from ZhengFang.model import Student, db, ClassSchedule, Class, YearGrade, OneLessonGrade, TermGrade

class ZhengFangSpider:

    def __init__(self,student,baseUrl="http://202.195.144.168/jndx"):
        reload(sys)
        sys.setdefaultencoding("utf-8")
        self.student = student
        self.baseUrl = baseUrl
        self.session = requests.session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'


    #含验证码登陆
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


    #绕过验证码登陆
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


    #获取学生基本信息
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


    #获取学生课表
    def getClassSchedule(self):
        self.session.headers['Referer'] = self.baseUrl+"/xs_main.aspx?xh="+self.student.studentnumber
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


    # 获取学生绩点
    def getStudentGrade(self):
        url = self.baseUrl + "/xscjcx.aspx?xh=" + self.student.studentnumber + "&xm=" + self.student.urlName + "&gnmkdm=N121605"
        self.session.headers['Referer'] = self.baseUrl + "/xs_main.aspx?xh=" + self.student.studentnumber
        response = self.session.get(url)
        __VIEWSTATE = get__VIEWSTATE(response)
        self.session.headers['Referer'] = url
        data = {
            "__EVENTTARGET":"",
            "__EVENTARGUMENT":"",
            "__VIEWSTATE":__VIEWSTATE,
            'hidLanguage':"",
            "ddlXN":"",
            "ddlXQ":"",
            "ddl_kcxz":"",
            "btn_zcj" : u"历年成绩".encode('gb2312', 'replace')
        }
        response = self.session.post(url,data=data)
        grades = getGrade(response)
        for onegrade in grades:
            year = onegrade["year"]
            term = onegrade["term"]
            try:
                yearGrade = YearGrade.get(YearGrade.year == year , YearGrade.student == self.student)
            except:
                yearGrade = YearGrade(year=year,student=self.student)
                yearGrade.save()
            try:
                termGrade = TermGrade.get(TermGrade.year == yearGrade , TermGrade.term == int(term))
            except:
                termGrade = TermGrade(year = yearGrade ,term = int(term))
                termGrade.save()
            try:
                gradePoint = float(onegrade["gradePonit"])
            except:
                gradePoint = None
            oneLessonGrade = OneLessonGrade(term=termGrade, name=onegrade["name"], type=onegrade["type"],
                                            credit=float(onegrade["credit"]), gradePoint=gradePoint, grade=onegrade["grade"])
            oneLessonGrade.save()
        print "获取成绩成功"


    # 计算每学期，每学年的绩点
    def calculateOneTermAndOneYearGPA(self):
        years = self.student.grades
        for year in years:
            terms = year.terms
            for term in terms:
                sumCredit = 0.0
                sumGrade = 0.0
                grades = term.lessonsGrades
                for grade in grades:
                        if grade.gradePoint == None:
                            continue
                        sumGrade = sumGrade +(grade.credit * grade.gradePoint)
                        sumCredit = sumCredit + grade.credit
                termGPA = float( '%.2f'% (sumGrade/sumCredit))
                term.termGPA = termGPA
                term.termCredit = sumCredit
                term.save()
            sumGrade = 0.0
            sumCredit = 0.0
            for term in terms:
                sumGrade += term.termGPA*term.termCredit
                sumCredit += term.termCredit
            year.yearGPA = float('%.2f' % (sumGrade/sumCredit))
            year.yearCredit = sumCredit
            year.save()
        print "绩点计算完毕"


if __name__ == "__main__":

    # 连接数据库，建立数据表
    try:
        db.connect()
        db.create_tables([Student, ClassSchedule,Class,YearGrade,TermGrade,OneLessonGrade])
    except:
        pass

    # 查找学生，若不存在则创建账号
    try:
        student = Student.get(Student.studentnumber == "xxxxxxxx")
    except Exception ,e:
        student = Student(studentnumber="xxxxxxxx", password="xxxxxxxxx")#用自己的教务系统账号密码
        student.save()

    spider = ZhengFangSpider(student,baseUrl="http://202.195.144.168/jndx") # 实例化爬虫
    spider.loginWithOutCode()
    if student.name is None:
        spider.getStudentBaseInfo()
    spider.getStudentGrade()
    spider.calculateOneTermAndOneYearGPA()
    spider.getClassSchedule()

