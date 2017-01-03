# encoding:utf-8
'''
Created on 2016-12-19
天津机场计费模块
小型客车（一型车、二型车）：每半小时2元
大型客车（三型车、四型车）：每半小时4元
不足半小时，按半小时计
过夜车辆，首个24小时60元封顶，以后每天50元封顶
@author: kcht
'''
from math import ceil

import time

from shhicparking.infrastructure.AbstractInfrastructures import ParkingFeeCalculator


class TjAirportFeeCalculator(ParkingFeeCalculator):
    def __init__(self):
        self.enterTime = 0
        self.exitTime = 0
        self.vehicleType = u'一型车'
        self.feePerHalfHour = 2
        self.fees = 2
        pass

    def getCurrentTollDetailTable(self):
        '''获取当前计费明细表'''  # 格式：[[开始时间,结束时间,计费方式,费率,金额],]
        return [[self.enterTime, self.exitTime, self.vehicleType, self.feePerHalfHour, self.fees], ]

    def getCurrentSum(self):
        '''获得当前计算金额数'''
        pass

    def reloadScript(self):
        '''重新载入计费脚本'''
        pass  # 规则简单，不需要计费脚本

    def getScriptFile(self):
        '''获取计费脚本文件'''
        pass  # 规则简单，不需要计费脚本

    def __calcType(self, vehicleType):
        """小型客车（一型车、二型车）,大型客车（三型车、四型车）"""
        if vehicleType == u'一型车' or vehicleType == u'二型车':
            return 2  # 小型客车，每半小时2元
        elif vehicleType == u'三型车' or vehicleType == u'四型车':
            return 4  # 大型客车，每半小时4元

    def __calcFees(self, halfHours, feePerHalfHour=2):
        fee = 0
        if halfHours <= 48:  # 第一天
            for h in range(halfHours):
                fee += feePerHalfHour
                if fee >= 60:
                    fee = 60
                    break
        elif 48 < halfHours:  # 后几天
            day = int(ceil(halfHours / 48.0)) - 1  # 天数
            fee = 60 + 50 * (day - 1)  # 初始费用
            for hh in range(halfHours - 48 * day):
                fee += feePerHalfHour
                if fee >= 60 + 50 * day:
                    fee = 60 + 50 * day
                    break
        return fee

    def calcActualParkingTimeAndFee(self, vehicleType, enterTime, exitTime, monthlyPayTimeInterval):
        '''计费并返回结果，返回值包含交易使用类型（错时停车、车位租赁，或""），及金额。'''
        # 入参enterTime,exitTime为毫秒时间戳
        # monthlyPayTimeInterval，车辆包月（错时停车）数据，格式为[[开始日期,结束日期,开始时间(距当天毫秒),结束时间],]
        self.enterTime = enterTime
        self.exitTime = exitTime
        self.vehicleType = vehicleType
        self.feePerHalfHour = self.__calcType(vehicleType)
        halfHours = int(ceil((exitTime - enterTime) / 1000 / 60 / 30.0))  # 不足半小时，按半小时计
        self.fees = self.__calcFees(halfHours, self.feePerHalfHour)
        return ["", self.fees]

    def calcFee(self, vehicleType, parkingTime, exitTime):
        '''计算停车费，入参为车型(汉字)及停车时间，出场时间'''
        return self.calcActualParkingTimeAndFee(vehicleType, exitTime - parkingTime, exitTime, [])[1]


# """
if __name__ == '__main__':
    tj = TjAirportFeeCalculator()
    print '--------------------------一型车-------------------------'
    print u"一型车(5.2小时)：%d" % tj.calcFee(
        u'一型车', 10.4 * 30 * 1000 * 60, time.time() * 1000 + 10.4 * 30 * 1000 * 60)  # 22
    for t in tj.getCurrentTollDetailTable():
        for tt in t:
            print tt
    print u"一型车(15.5小时)：%d" % tj.calcFee(
        u'一型车', 31 * 30 * 1000 * 60, time.time() * 1000 + 31 * 30 * 1000 * 60)  # 60
    print u"一型车(36.5小时)：%d" % tj.calcFee(
        u'一型车', 73 * 30 * 1000 * 60, time.time() * 1000 + 73 * 30 * 1000 * 60)  # 110
    print u"一型车(49.2小时)：%d" % tj.calcFee(
        u'一型车', 98.4 * 30 * 1000 * 60, time.time() * 1000 + 98.4 * 30 * 1000 * 60)  # 116

    print '--------------------------二型车-------------------------'
    print u"二型车(33.6小时)：%d" % tj.calcFee(
        u'二型车', 67.2 * 30 * 1000 * 60, time.time() * 1000 + 67.2 * 30 * 1000 * 60)  # 100
    for t in tj.getCurrentTollDetailTable():
        for tt in t:
            print tt

    print '--------------------------三型车-------------------------'
    print u"三型车(5小时)：%d" % tj.calcFee(
        u'三型车', 10 * 30 * 1000 * 60, time.time() * 1000 + 10 * 30 * 1000 * 60)  # 40
    for t in tj.getCurrentTollDetailTable():
        for tt in t:
            print tt
    print u"三型车(7.5小时)：%d" % tj.calcFee(
        u'三型车', 15 * 30 * 1000 * 60, time.time() * 1000 + 15 * 30 * 1000 * 60)  # 60
    print u"三型车(30.4小时)：%d" % tj.calcFee(
        u'三型车', 60.8 * 30 * 1000 * 60, time.time() * 1000 + 60.8 * 30 * 1000 * 60)  # 110
    print u"三型车(49.2小时)：%d" % tj.calcFee(
        u'三型车', 98.4 * 30 * 1000 * 60, time.time() * 1000 + 98.4 * 30 * 1000 * 60)  # 122

    print '--------------------------四型车-------------------------'
    print u"四型车(29小时)：%d" % tj.calcFee(
        u'四型车', 58 * 30 * 1000 * 60, time.time() * 1000 + 58 * 30 * 1000 * 60)  # 100
    for t in tj.getCurrentTollDetailTable():
        for tt in t:
            print tt
# """
