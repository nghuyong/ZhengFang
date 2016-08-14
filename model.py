# author: HuYong
# coding=utf-8

from peewee import *

db = SqliteDatabase('ZhengFang.db')


class Student(Model):
    name = CharField(null=True)
    urlName = CharField(null=True)
    studentnumber = CharField(null=True)
    password = CharField(null=True)
    idCardNumber = CharField(null=True)
    sex = CharField(null=True)
    enterSchoolTime = CharField(null=True)
    birthsday = CharField(null=True)
    highschool = CharField(null=True)
    nationality = CharField(null=True)
    hometown = CharField(null=True)
    politicsStatus = CharField(null=True)
    college= CharField(null=True)
    major = CharField(null=True)
    classname = CharField(null=True)
    gradeClass = CharField(null=True)

    class Meta:
        database = db

class ClassSchedule(Model):
    student = ForeignKeyField(Student,related_name="classSchedule")
    year = CharField(null=True)
    term = IntegerField(null=True)

    class Meta:
        database = db


class Class(Model):
    schedule = ForeignKeyField(ClassSchedule,related_name="classes")
    name = CharField(null=True)
    type = CharField(null=True)
    timeInTheWeek = CharField(null=True)
    timeInTheDay = CharField(null=True)
    timeInTheTerm = CharField(null=True)
    teacher = CharField(null=True)
    location = CharField(null=True)

    class Meta:
        database = db