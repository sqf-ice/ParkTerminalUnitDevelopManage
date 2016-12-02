#encoding:utf-8
'''
Created on 2015-6-19
日期时间工具
@author: user
'''

import time,datetime

def nowStr():
    '''当前时间字符串'''
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def simpleNowStr():
    '''简易当前字符串'''
    return time.strftime('%m-%d %H:%M',time.localtime(time.time()))
    
def nowTime():
    '''当前时间戳'''
    return int(time.time()*1000)

def dtStr(timeInMs):
    '''毫秒数转为完整日期时间字符串'''
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(timeInMs/1000))

def toInterval(timeInMs):
    '''换算为时间间隔描述'''
    tInM = int(timeInMs/60000)
    return u"%d小时%d分钟"%(tInM/60,tInM%60)

def toHM(timeInMs):
    '''从距0:0:0的毫秒数换算为字符串表示'''
    tInM = int(timeInMs/60000)
    return u"%.2d:%.2d"%(tInM/60,tInM%60)

def HMStr(timeInMs):
    '''毫秒转换成时分字符串（忽略日期部分）'''
    return time.strftime('%H:%M',time.localtime(timeInMs/1000))
    
def msToDt(timeInMs):
    '''毫秒转换成只含日期的字符串'''
    return time.strftime('%Y-%m-%d',time.localtime(timeInMs/1000))

def msInDay(timeInMs):
    '''毫秒数转换成距离今天00:00:00的毫秒数'''
    a = time.localtime(timeInMs/1000)
    b = time.mktime(datetime.date(a.tm_year,a.tm_mon,a.tm_mday).timetuple())
    return int(timeInMs-b*1000)


def getThisDay(timeInMs):
    '''获得今天0:00:00的时间戳'''
    a = time.localtime(timeInMs/1000)
    b = time.mktime(datetime.date(a.tm_year,a.tm_mon,a.tm_mday).timetuple())
    return int(b*1000)

def timeDescToDailyMs(timeDesc):
    '根据时间描述08:00转换成距离当天00:00:00的毫秒数'
    t = timeDesc.split(":")
    if len(t) == 2:return (int(t[0])*3600 + int(t[1])*60)*1000
    elif len(t) == 3:return (int(t[0])*3600 + int(t[1])*60 + int(t[2]))*1000
    
    