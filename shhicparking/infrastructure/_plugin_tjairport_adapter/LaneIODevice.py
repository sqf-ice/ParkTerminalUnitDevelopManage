# encoding:utf-8
'''
Created on 2016-11-23
车道机IO设备
'''
import ctypes
import os
import time

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
        try:
            dll_path = os.path.join(os.path.dirname(__file__) + '/../../../driver/')
            ctypes.cdll.LoadLibrary(dll_path + 'WinIo32.dll')
            self.dllIO = ctypes.cdll.LoadLibrary(dll_path + 'F75111.dll')
            self.dllIO.F75111_SetAddress(0x9c)
            self.initF75111 = self.dllIO.F75111_Init()
            time.sleep(2)
            if not self.initF75111:
                print "F75111({getAddr})初始化失败!".format(getAddr=self.dllIO.F75111_GetAddress())
        except:
            raise Exception("F75111.dll异常!")

    def hasVehicle(self, coilNum):
        "地感上是否有车，入参是地感编号1-3"  # 有车返回True，没车返回False
        if self.initF75111:
            get = self.dllIO.F75111_GetDigitalInput()
            rtn = {
                1: lambda x: get & self.COIL_INPUT_VALUES['FIRST_COIL'],
                2: lambda x: get & self.COIL_INPUT_VALUES['SECOND_COIL'],
                3: lambda x: get & self.COIL_INPUT_VALUES['THIRD_COIL']
            }[coilNum](get)
            return True if rtn is 0 else False

    def isVehicleComes(self, coilNum, timeWnd=2):
        "是否有车压上地感（上跳沿）"
        # 入参是地感编号，和时间窗口（秒）。即检查timeWnd时间内，地感coilNum是否存在一个上跳沿，如果有，返回True，否则返回False
        if self.initF75111:
            try:
                back = self.hasVehicle(coilNum)
                time.sleep(timeWnd)
                front = self.hasVehicle(coilNum)
                return True if (back is False and front is True) else False
            except:
                raise Exception("LaneIODevice.isVehicleComes Exception")

    def isVehicleLeaves(self, coilNum, timeWnd=2):
        "是否有车离开地感（下跳沿）"
        # 入参是地感编号，和时间窗口（秒）。即检查timeWnd时间内，地感coilNum是否存在一个下跳沿，如果有，返回True，否则返回False
        if self.initF75111:
            try:
                back = self.hasVehicle(coilNum)
                time.sleep(timeWnd)
                front = self.hasVehicle(coilNum)
                return True if (back is True and front is False) else False
            except:
                raise Exception("LaneIODevice.isVehicleLeaves Exception")

    def notifyNormal(self):
        "通知雨棚灯显示正常"
        if self.initF75111:
            try:
                self.dllIO.F75111_SetDigitalOutput(self.COIL_OUTPUT_VALUES['NORMAL'])
            except:
                raise Exception("LaneIODevice.notifyNormal Exception")
            finally:
                time.sleep(0.5)

    def notifyWrong(self):
        "通知雨棚灯显示异常"
        if self.initF75111:
            try:
                self.dllIO.F75111_SetDigitalOutput(self.COIL_OUTPUT_VALUES['WRONG'])
            except:
                raise Exception("LaneIODevice.notifyWrong Exception")
            finally:
                time.sleep(0.5)

    def liftTheRail(self):
        '''抬杆'''
        if self.initF75111:
            try:
                self.dllIO.F75111_SetDigitalOutput(self.COIL_OUTPUT_VALUES['LIFT_RAIL'])
            except:
                raise Exception("LaneIODevice.liftTheRail Exception")
            finally:
                time.sleep(3)

    def dropTheRail(self):
        '''落杆'''
        if self.initF75111:
            try:
                self.dllIO.F75111_SetDigitalOutput(self.COIL_OUTPUT_VALUES['DROP_RAIL'])
            except:
                raise Exception("LaneIODevice.dropTheRail Exception")
            finally:
                time.sleep(3)


"""
if __name__ == "__main__":
    # dv = LaneIODevice("aa",{u"设备串口号":"com1",xxxxxx})
    props = {u"触发线圈输入端子": 1, u"存在线圈输入端子": 2, u"停止线圈输入端子": 3,
             u"雨棚灯控制端子": 1, u"道闸抬起控制端子": 2, u"道闸落下控制端子": 3}

    dv = LaneIODevice("aa", props)
    print "-----------------------------------------"
    print "hasVehicle(1):{}".format(dv.hasVehicle(1))
    print "hasVehicle(2):{}".format(dv.hasVehicle(2))
    print "hasVehicle(3):{}".format(dv.hasVehicle(3))

    print "-----------------------------------------"
    print "isVehicleComes(1):{}".format(dv.isVehicleComes(1))
    print "isVehicleComes(2):{}".format(dv.isVehicleComes(2))
    print "isVehicleComes(3):{}".format(dv.isVehicleComes(3))

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
