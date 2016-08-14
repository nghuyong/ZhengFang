# author: HuYong
# coding=utf-8

from peewee import *

db = SqliteDatabase('ZhengFang.db')


class Student(Model):
    name = CharField(null=True)  # 姓名
    urlName = CharField(null=True)  # url编码后的姓名
    studentnumber = CharField(null=True)  # 学号
    password = CharField(null=True)  # 教务系统密码
    idCardNumber = CharField(null=True)  # 身份证号
    sex = CharField(null=True)  # 性别
    enterSchoolTime = CharField(null=True)  # 入学时间
    birthsday = CharField(null=True)  # 出生日期
    highschool = CharField(null=True)  # 毕业中学
    nationality = CharField(null=True)  # 名族
    hometown = CharField(null=True)  # 籍贯
    politicsStatus = CharField(null=True)  # 政治面貌
    college = CharField(null=True)  # 学院
    major = CharField(null=True)  # 专业
    classname = CharField(null=True)  # 所在班级
    gradeClass = CharField(null=True)  # 年级

    class Meta:
        database = db


class ClassSchedule(Model):
    student = ForeignKeyField(Student, related_name="classSchedule")  # 学生
    year = CharField(null=True)  # 年度
    term = IntegerField(null=True)  # 学期

    class Meta:
        database = db


class Class(Model):
    schedule = ForeignKeyField(ClassSchedule, related_name="classes")  # 归属课表
    name = CharField(null=True)  # 课程名称
    type = CharField(null=True)  # 课程性质
    timeInTheWeek = CharField(null=True)  # 星期几
    timeInTheDay = CharField(null=True)  # 第几节课
    timeInTheTerm = CharField(null=True)  # 上课周数
    teacher = CharField(null=True)  # 授课教师
    location = CharField(null=True)  # 授课地点

    class Meta:
        database = db


class YearGrade(Model):
    student = ForeignKeyField(Student, related_name="grades")  # 归属学生
    year = CharField(null=True) # 学年
    yearGPA = DoubleField(null=True)  # 学年GPA
    yearCredit = DoubleField(null=True)  # 学年总学分

    class Meta:
        database = db


class TermGrade(Model):
    year = ForeignKeyField(YearGrade,related_name="terms")  # 归属学年
    term = IntegerField(null=True) # 学期
    termGPA = DoubleField(null=True) # 学期GPA
    termCredit = DoubleField(null=True) #学期总学分

    class Meta:
        database = db



class OneLessonGrade(Model):
    term = ForeignKeyField(TermGrade, related_name="lessonsGrades")  # 归属学期
    name = CharField(null=True)  # 课程名
    type = CharField(null=True)  # 课程性质
    credit = DoubleField(null=True)  # 学分
    gradePoint = DoubleField(null=True)  # 绩点
    grade = CharField(null=True)  # 成绩

    class Meta:
        database = db