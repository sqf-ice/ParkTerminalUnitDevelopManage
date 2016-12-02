# encoding:utf-8
'''
Created on 2016-9-27

@author: user
'''

from kcht_complex_etc.infras import *
from shhicparking.infrastructure.AbstractInfrastructures import *
import time
from threading import Thread, RLock
from PyQt4 import QtCore, QtGui, uic


class CETC_GroundCoils_Mock(AbstractInfrastructure, CETC_GroundCoils):
    class MockGroundCoilThread(Thread):
        def __init__(self):
            Thread.__init__(self)
            self.coilMap = [False, False, False, False]
            self.lock = RLock()

        def run(self):
            i = 0
            while True:
                i += 1
                self.lock.acquire()
                self.coilMap = [False, False, False, False]
                self.coilMap[i % 4] = True
                self.lock.release()
                if self.coilMap[2]:
                    time.sleep(1)
                else:
                    time.sleep(1)

        def __getitem__(self, indx):
            self.lock.acquire()
            try:
                return self.coilMap[indx - 1]
            finally:
                self.lock.release()

    def __init__(self, infrasId, props):
        AbstractInfrastructure.__init__(self, infrasId, props)
        self.changeTime = time.time()
        self.current = 1
        self.mc = CETC_GroundCoils_Mock.MockGroundCoilThread()
        self.mc.start()

    def hasVehicle(self, coilNum):
        "地感上是否有车，入参是地感编号1-3"  # 有车返回True，没车返回False
        return self.mc[coilNum]

    def isVehicleComes(self, coilNum, timeWnd=2):
        "是否有车压上地感（上跳沿）"  # 入参是地感编号，和时间窗口（秒）。即检查timeWnd时间内，地感coilNum是否存在一个上跳沿，如果有，返回True，否则返回False
        return self.mc[coilNum]

    def isVehicleLeaves(self, coilNum, timeWnd=2):
        "是否有车离开地感（下跳沿）"  # 入参是地感编号，和时间窗口（秒）。即检查timeWnd时间内，地感coilNum是否存在一个下跳沿，如果有，返回True，否则返回False
        return not self.mc[coilNum]


class CETC_Signals_Mock(AbstractInfrastructure, CETC_Alarm, CETC_CanopyLights):
    def __init__(self, infrasId, props):
        AbstractInfrastructure.__init__(self, infrasId, props)

    def openAlarm(self, alarmNo=0):
        "打开报警器"  # 入参可选，是报警器号

    def closeAlarm(self, alarmNo=0):
        "关闭报警器"  # 入参可选，是报警器号

    def notifyNormal(self):
        "通知雨棚灯显示正常"

    def notifyWrong(self):
        "通知雨棚灯显示异常"


class CETC_Infras_Mock(AbstractInfrastructure, Camera, PhotoCapture, PlatePhotoParser, Guardrail, LED, Speaker):
    def __init__(self, infrasId, props):
        AbstractInfrastructure.__init__(self, infrasId, props)

    def startVedio(self, uiFrame):
        '''开始视频'''

    def stopVedio(self):
        '''结束视频'''

    def capturePhoto(self):
        '''触发抓拍'''
        try:
            x = open("config/mockSlotMap.png", "rb")
            return x.read(50 * 1024)
        finally:
            x.close()

    def parsePlateNo(self, photo=None):
        '''号牌识别，返回车牌和车型，入参可能是图片，也可能空（硬识别）'''
        return u"津A%.5d" % (time.time() % 1000), u"小型车"

    #        return None,None

    def liftTheRail(self):
        '''抬杆'''

    def dropTheRail(self):
        '''落杆'''

    def showOnLed(self, message):
        '''LED上显示消息'''
        print "[LED]", message

    def speak(self, message):
        '''说话'''
