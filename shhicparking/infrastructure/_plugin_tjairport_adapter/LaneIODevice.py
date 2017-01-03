# encoding:utf-8
'''
Created on 2016-11-23
车道机IO设备
'''
import ctypes
import os
import threading

import time
from thread import start_new_thread

from kcht_complex_etc.infras import *
from shhicparking.infrastructure.AbstractInfrastructures import *


class LaneIODevice(AbstractInfrastructure, CETC_GroundCoils, CETC_CanopyLights, Guardrail):
    def __init__(self, infrasId, props):
        AbstractInfrastructure.__init__(self, infrasId, props)
        self.COIL_INPUT_MAP = {1: int(props[u"触发线圈输入端子"]), 2: int(props[u"存在线圈输入端子"]), 3: int(props[u"停止线圈输入端子"])}
        """
        self.OUTPUT_MAP = {"pass": int(props[u"雨棚灯控制端子"]),  # 通行灯开关输出端子
                           "lift_rail": int(props[u"道闸抬起控制端子"]), "drop_rail": int(props[u"道闸落下控制端子"])  # 道闸开关输出端子
                           }
        """
        "F75111.dll初始化"
        self.COIL_INPUT_VALUES = {'FIRST_COIL': 0x10, 'SECOND_COIL': 0x20,  # 四线圈输入
                                  'THIRD_COIL': 0x40, 'FORTH_COIL': 0x80}
        self.COIL_OUTPUT_VALUES = {'NORMAL': 0x01, 'WRONG': 0x00,
                                   'LIFT_RAIL': 0x10, 'DROP_RAIL': 0x20}  # 抬杆落杆}
        self.inputBuffer = dict.fromkeys(range(4), False)  # 输入缓存，key:X编号，从0到3；value，通为True，断为False
        self.inputJumpTime = dict.fromkeys(range(4), 0)  # 跳变时间，key:X编号，从0到3；value，毫秒时间戳
        try:
            dll_path = os.path.join(os.path.dirname(__file__) + '/../../../driver/')
            ctypes.cdll.LoadLibrary(dll_path + 'WinIo.dll')
            self.dllIO = ctypes.CDLL(dll_path + 'IORW.dll')
            self.io = self.dllIO.WinIoInit()
            if not self.io:
                print "LaneIODevice.WinIoInit失败:" + str(self.io)
            self.initF75111 = self.dllIO.F75111Init()
            if not self.initF75111:
                print "LaneIODevice.initF75111失败:" + str(self.initF75111)
            else:
                print "LaneIODevice.initF75111成功!"
                self.value = 0xff
                threading.Thread(target=self.dioRead, ).start()
                threading.Thread(target=self.readValue, ).start()
        except Exception, e:
            print "LaneIODevice dll 异常:" + str(e)

    def dioRead(self):
        while True:
            try:
                self.value = self.dllIO.DIO_Read()
                # print bin(self.value)
            finally:
                time.sleep(0.1)

    def hasVehicle(self, coilNum):
        "地感上是否有车，入参是地感编号1-3"  # 有车返回True，没车返回False
        if self.initF75111:
            # get = self.dllIO.DIO_Read()
            # print bin(get)
            rtn = {
                1: lambda x: self.value & self.COIL_INPUT_VALUES['FIRST_COIL'],
                2: lambda x: self.value & self.COIL_INPUT_VALUES['SECOND_COIL'],
                3: lambda x: self.value & self.COIL_INPUT_VALUES['THIRD_COIL']
            }[coilNum](self.value)
            return True if rtn is 0 else False
            # if rtn is 0:
            #     return True
            # else:
            #     return False

    def isJumps(self, coilNum, timeWnd, currentTime=None):
        # 检查在时间窗口内是否有跳变
        if currentTime is None:
            currentTime = int(time.time() * 1000)
        return currentTime - self.inputJumpTime[coilNum] < timeWnd * 1000

    def readValue(self):
        while True:
            try:
                get = self.value >> 4
                # print bin(get)
                if get is not None:
                    mask = 0b00000001
                    for i in range(4):
                        currentValue = not bool(get & mask)
                        # print currentValue
                        if self.inputBuffer[i] != currentValue:
                            self.inputJumpTime[i] = int(time.time() * 1000)
                            self.inputBuffer[i] = currentValue
                        mask <<= 1
            finally:
                time.sleep(0.1)

    def isVehicleComes(self, coilNum, timeWnd=2):
        "是否有车压上地感（上跳沿）"
        # 入参是地感编号，和时间窗口（秒）。即检查timeWnd时间内，地感coilNum是否存在一个上跳沿，如果有，返回True，否则返回False
        return self.hasVehicle(coilNum) and self.isJumps(coilNum - 1, timeWnd)
        pass

    def isVehicleLeaves(self, coilNum, timeWnd=2):
        "是否有车离开地感（下跳沿）"
        # 入参是地感编号，和时间窗口（秒）。即检查timeWnd时间内，地感coilNum是否存在一个下跳沿，如果有，返回True，否则返回False
        # return (not self.dv[coilNum - 1]) and self.dv.isJumps(coilNum - 1, timeWnd)
        return (not self.hasVehicle(coilNum)) and self.isJumps(coilNum - 1, timeWnd)

    def notifyNormal(self):
        "通知雨棚灯显示正常"
        if self.initF75111:
            try:
                self.dllIO.DIO_Write(self.COIL_OUTPUT_VALUES['NORMAL'])
            except Exception:
                print "LaneIODevice.notifyNormal Exception"

    def notifyWrong(self):
        "通知雨棚灯显示异常"
        if self.initF75111:
            try:
                self.dllIO.DIO_Write(self.COIL_OUTPUT_VALUES['WRONG'])
            except Exception:
                print "LaneIODevice.notifyWrong Exception"

    def liftTheRail(self):
        '''抬杆'''
        if self.initF75111:
            try:
                self.dllIO.DIO_Write(self.COIL_OUTPUT_VALUES['LIFT_RAIL'])
            except Exception:
                print "LaneIODevice.liftTheRail Exception"

    def dropTheRail(self):
        '''落杆'''
        if self.initF75111:
            try:
                self.dllIO.DIO_Write(self.COIL_OUTPUT_VALUES['DROP_RAIL'])
            except Exception:
                print "LaneIODevice.dropTheRail Exception"


# """
if __name__ == "__main__":
    # dv = LaneIODevice("aa",{u"设备串口号":"com1",xxxxxx})

    props = {u"触发线圈输入端子": 1, u"存在线圈输入端子": 2, u"停止线圈输入端子": 3,
             u"雨棚灯控制端子": 1, u"道闸抬起控制端子": 2, u"道闸落下控制端子": 3}

    dv = LaneIODevice("aa", props)
    print "-----------------------------------------"


    def testComes():
        while True:
            print "isVehicleComes(1):{}".format(dv.isVehicleComes(1))
            print "isVehicleComes(2):{}".format(dv.isVehicleComes(2))
            print "isVehicleComes(3):{}".format(dv.isVehicleComes(3))
            time.sleep(1)


    def testLeaves():
        while True:
            print "isVehicleLeaves(1):{}".format(dv.isVehicleLeaves(1))
            print "isVehicleLeaves(2):{}".format(dv.isVehicleLeaves(2))
            print "isVehicleLeaves(3):{}".format(dv.isVehicleLeaves(3))
            time.sleep(1)

    # threading.Thread(target=testComes, ).start()
    # threading.Thread(target=testLeaves, ).start()

    # print "isVehicleLeaves(1):{}".format(dv.isVehicleLeaves(1))
    # print "isVehicleLeaves(2):{}".format(dv.isVehicleLeaves(2))
    # print "isVehicleLeaves(3):{}".format(dv.isVehicleLeaves(3))
    # print "isVehicleComes(2):{}".format(dv.isVehicleComes(2))
    # print "isVehicleComes(3):{}".format(dv.isVehicleComes(3))
"""
    print "-----------------------------------------"
    print "hasVehicle(1):{}".format(dv.hasVehicle(1))
    print "hasVehicle(2):{}".format(dv.hasVehicle(2))
    print "hasVehicle(3):{}".format(dv.hasVehicle(3))



    print "-----------------------------------------"
    print "isVehicleLeaves(1):{}".format(dv.isVehicleLeaves(1))
    print "isVehicleLeaves(2):{}".format(dv.isVehicleLeaves(2))
    print "isVehicleLeaves(3):{}".format(dv.isVehicleLeaves(3))

    print "-----------------------------------------"
    print "liftTheRail():{}".format(dv.liftTheRail())
    time.sleep(5)
    print "dropTheRail():{}".format(dv.dropTheRail())

    print "-----------------------------------------"
    print "notifyNormal():{}".format(dv.notifyNormal())
    time.sleep(2)
    print "notifyWrong():{}".format(dv.notifyWrong())

    print "-----------------------------------------"
    dv.dllIO.F75111_Shutdown()
"""
# """
