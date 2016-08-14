# author: HuYong
# coding=utf-8
from bs4 import BeautifulSoup
from lxml import etree

def getInfoFromHtml(response, xpath):
    content = response.content.decode('gb2312')
    selector = etree.HTML(content)
    infor = selector.xpath(xpath)[0]
    return infor

def getStudentInfor(response):
    html = response.content.decode("gb2312")
    soup = BeautifulSoup(html.decode("utf-8"), "html5lib")
    d = {}
    d["studentnumber"] = soup.find(id="xh").string
    d["idCardNumber"] = soup.find(id="lbl_sfzh").string
    d["name"] = soup.find(id="xm").string
    d["sex"] = soup.find(id="lbl_xb").string
    d["enterSchoolTime"] = soup.find(id="lbl_rxrq").string
    d["birthsday"] = soup.find(id="lbl_csrq").string
    d["highschool"] = soup.find(id="lbl_byzx").string
    d["nationality"] = soup.find(id="lbl_mz").string
    d["hometown"] = soup.find(id="lbl_jg").string
    d["politicsStatus"] = soup.find(id="lbl_zzmm").string
    d["college"] = soup.find(id="lbl_xy").string
    d["major"] = soup.find(id="lbl_zymc").string
    d["classname"] = soup.find(id="lbl_xzb").string
    d["gradeClass"] = soup.find(id="lbl_dqszj").string
    return d

def getClassScheduleFromHtml(response):
    html = response.content.decode("gb2312")
    soup = BeautifulSoup(html.decode("utf-8"), "html5lib")
    __VIEWSTATE = soup.findAll(name="input")[2]["value"]
    trs = soup.find(id="Table1").find_all('tr')
    classes = []
    for tr in trs:
        tds = tr.find_all('td')
        for td in tds:
            if td.string == None:
                oneClassKeys = ["name", "type", "time", "teacher", "location"]
                oneClassValues = []
                for child in td.children:
                    if child.string != None:
                        oneClassValues.append(child.string)
                while len(oneClassValues) < len(oneClassKeys):
                    oneClassValues.append("")
                oneClass = dict((key, value) for key, value in zip(oneClassKeys, oneClassValues))
                oneClass["timeInTheWeek"] = oneClass["time"].split("{")[0][:2]
                oneClass["timeInTheDay"] = oneClass["time"].split("{")[0][2:]
                oneClass["timeInTheTerm"] = oneClass["time"].split("{")[1][:-1]
                classes.append(oneClass)
    return {"classes":classes,"__VIEWSTATE" :__VIEWSTATE}