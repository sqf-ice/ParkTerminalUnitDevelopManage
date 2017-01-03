# encoding: utf-8


"""
@version: 1.0
@file: LaneIOBoard.py
@time: 2016/12/26 16:00
@desc: 车道逻辑的IO板实现
"""
from threading import Thread, RLock
import time
import serial

from kcht_complex_etc.infras import CETC_GroundCoils, CETC_CanopyLights
from shhicparking.infrastructure.AbstractInfrastructures import AbstractInfrastructure, Guardrail

CMD_PROTOTYPE = [0x00, 0x5A, 0x56, 0x00, None, None, 0x00, 0x00, None]


class Longgang8I8OBoardDevice(Thread):
    """龙岗IO板8I8O的驱动"""

    def __init__(self, initParam):
        Thread.__init__(self)
        self.ioBoardCom = initParam["ioBoardCom"]
        self.serialPortLock = RLock()
        self.runnable = False
        self.buttonTriggerStartTime = 0  # 按钮触发开始时间，在时间窗口内，不再响应
        self.inputBuffer = dict.fromkeys(range(8), False)  # 输入缓存，key:X编号，从0到7；value，通为True，断为False
        self.inputJumpTime = dict.fromkeys(range(8), 0)  # 跳变时间，key:X编号，从0到7；value，毫秒时间戳

    def initResource(self):
        try:
            self.serialPortLock.acquire()
            if not self.runnable:
                self.boardSerial = serial.Serial(port=self.ioBoardCom, baudrate=9600, timeout=2)
                self.boardSerial.setRTS(False)
                self.runnable = True
                self.start()
        except:
            raise Exception(u"初始化控制IO板失败，请检查设置并重启软件")
        finally:
            self.serialPortLock.release()

    def retrive(self):
        self.runnable = False
        self.boardSerial.close()

    def run(self):
        while True:
            try:
                self.__readAndFillBuffer()
            except Exception, e:
                print e
            finally:
                time.sleep(0.01)

    def __readAndFillBuffer(self):
        '''读取IO板的所有输入（X）状态并缓存'''
        self.serialPortLock.acquire()
        try:
            self.boardSerial.write(bytearray([0x00, 0x5A, 0x56, 0x00, 0x07, 0x00, 0x00, 0x00, 0xB7]))
            rd = self.boardSerial.read(9)
        finally:
            self.serialPortLock.release()
        if rd == "": return
        if self.checkSum(rd[:-1]) != ord(rd[-1]):
            print 'RS485 CHECK SUM ERROR'
            return
        # print "".join(["%.2X"%ord(c) for c in rd])
        if rd is not None:
            mask = 0b00000001
            is_07 = ord(rd[7])
            for i in range(8):
                currentValue = not bool(is_07 & mask)
                if self.inputBuffer[i] != currentValue:
                    self.inputJumpTime[i] = int(time.time() * 1000)
                    self.inputBuffer[i] = currentValue
                mask <<= 1
                #        print ",".join([("H" if x else "L") for x in self.inputBuffer])

    def __getitem__(self, x):
        '''获取输入的值，x为X（输入）编号，0到7'''
        try:
            # self.serialPortLock.acquire()
            return self.inputBuffer[x] if x in self.inputBuffer else False
        finally:
            # self.serialPortLock.release()
            pass

    def __setitem__(self, y, value):
        '''输出控制，y为Y(输出)编号，0-7，value为True表示通，False表示断'''
        cmd = [x for x in CMD_PROTOTYPE]
        cmd[4] = 0x01 if value else 0x02  # 命令：打开
        cmd[5] = y + 1  # IO编号1-8
        cmd[8] = self.checkSum(cmd[:-1])
        cmdArray = bytearray(cmd)
        self.serialPortLock.acquire()
        try:
            self.boardSerial.write(cmdArray)
            self.boardSerial.read(9)
        finally:
            self.serialPortLock.release()

    def pulseTrigger(self, port):
        '''脉冲触发'''
        self[port] = True
        time.sleep(0.5)
        self[port] = False

    def isJumps(self, x, timeWnd, currentTime=None):
        # 检查在时间窗口内是否有跳变
        if currentTime is None:
            currentTime = int(time.time() * 1000)
        return currentTime - self.inputJumpTime[x] < timeWnd * 1000

    def checkSum(self, frame):
        '''计算校验和'''
        csum = 0
        for i in frame:
            if type(i) == str:
                csum += ord(i)
            else:
                csum += i
        return csum % 256


class LaneIOBoard(AbstractInfrastructure, CETC_GroundCoils, CETC_CanopyLights, Guardrail):
    def __init__(self, infrasId, props):
        AbstractInfrastructure.__init__(self, infrasId, props)
        "IO板初始化"
        self.dv = Longgang8I8OBoardDevice({"ioBoardCom": props[u"IO板串口号"]})
        self.dv.initResource()

    def hasVehicle(self, coilNum):
        "地感上是否有车，入参是地感编号1-3"  # 有车返回True，没车返回False
        return self.dv[coilNum - 1]

    def isVehicleComes(self, coilNum, timeWnd=2):
        "是否有车压上地感（上跳沿）"
        # 入参是地感编号，和时间窗口（秒）。即检查timeWnd时间内，地感coilNum是否存在一个上跳沿，如果有，返回True，否则返回False
        return self.dv[coilNum - 1] and self.dv.isJumps(coilNum - 1, timeWnd)

    def isVehicleLeaves(self, coilNum, timeWnd=2):
        "是否有车离开地感（下跳沿）"
        # 入参是地感编号，和时间窗口（秒）。即检查timeWnd时间内，地感coilNum是否存在一个下跳沿，如果有，返回True，否则返回False
        return (not self.dv[coilNum - 1]) and self.dv.isJumps(coilNum - 1, timeWnd)

    def notifyNormal(self):
        "通知雨棚灯显示正常,输出LED1灭"
        self.dv[0] = False

    def notifyWrong(self):
        "通知雨棚灯显示异常,输出LED1亮"
        self.dv[0] = True

    def liftTheRail(self):
        '''抬杆，输出LED3亮，输出LED4灭'''
        self.dv[2] = True
        self.dv[3] = False

    def dropTheRail(self):
        '''落杆,输出LED3灭，输出LED4亮'''
        self.dv[2] = False
        self.dv[3] = True


if __name__ == '__main__':
    props = {u"触发线圈输入端子": 1, u"存在线圈输入端子": 2, u"停止线圈输入端子": 3,
             u"雨棚灯控制端子": 1, u"道闸抬起控制端子": 2, u"道闸落下控制端子": 3}

    dv = LaneIOBoard(("aa", props))

    print "-----------------------------------------"


    def test():
        while True:
            print "Starting................"
            print "isVehicleComes(1):{}".format(dv.isVehicleComes(1))
            time.sleep(2)
            print "isVehicleComes(2):{}".format(dv.isVehicleComes(2))
            time.sleep(2)
            print "isVehicleLeaves(3):{}".format(dv.isVehicleLeaves(3))
            time.sleep(2)
            print "isVehicleLeaves(4):{}".format(dv.isVehicleLeaves(4))
            time.sleep(2)

            print "hasVehicle(1):{}".format(dv.hasVehicle(1))
            time.sleep(1)
            dv.notifyNormal()
            time.sleep(1)
            dv.notifyWrong()
            time.sleep(2)

            dv.liftTheRail()
            time.sleep(1)
            dv.dropTheRail()
            time.sleep(5)
