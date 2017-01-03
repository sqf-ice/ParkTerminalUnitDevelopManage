# encoding:utf-8
'''
Created on 2016-11-23
车道LED显示器
@author: kcht
'''
import serial
import time

from kcht_complex_etc.infras import *
from shhicparking.infrastructure.AbstractInfrastructures import *


class LaneLedIntegratedDevice(AbstractInfrastructure, CETC_Alarm, LED):
    def __init__(self, infrasId, props):
        AbstractInfrastructure.__init__(self, infrasId, props)
        self.devicePort = props[u"设备串口号"]
        self.idleMessage = props[u"空闲消息"]

        "串口初始化"
        try:
            self.com = serial.Serial(self.devicePort, 9600, timeout=5)
        except Exception:
            print u"串口初始化失败！"

    def showOnLed(self, message):
        '''LED上显示消息'''
        # 整屏要显示的汉字或字符ASII码,字节数小于255内不限, 但超过显示屏显示长度部分将不显示
        message = message.replace("\\n", "\n")
        frame = [0x0a, 0x43]
        for x in ('' + message).split('\n'):
            if 0 and x.encode('gb2312').__len__() > 16:
                raise Exception("LaneLedIntegratedDevice.showOnLed:显示字符超出范围")
            while x.encode('gb2312').__len__() < 16:
                x += ' '
            print x
            frame.extend(x.encode('gb2312'))
        frame.append(0x0d)
        self.com.write(frame)
        time.sleep(0.1)

    def showIdleMsgOnLed(self):
        '''LED上显示默认空闲消息'''  # 可由子类重写，也可以不实现
        self.showOnLed(self.idleMessage)

    def openAlarm(self, alarmNo=1):
        "打开报警器,同步控制通行车道信号灯"  # 入参可选，是报警器号
        print "should open alarm and make the light red cross"
        alarm_frame = [0x0A, 0x50, alarmNo, 0x00, 0x0D]
        signal_frame = [0x0A, 0x51, 0x01, 0x01, 0x0D]
        self.com.write(alarm_frame)
        self.com.write(signal_frame)

    def closeAlarm(self, alarmNo=1):
        "关闭报警器,同步控制通行车道信号灯"  # 入参可选，是报警器号
        alarm_frame = [0x0a, 0x50, alarmNo, 0x01, 0x0d]
        signal_frame = [0x0A, 0x51, 0x01, 0x00, 0x0D]
        self.com.write(alarm_frame)
        self.com.write(signal_frame)


# """
if __name__ == '__main__':
    dv = LaneLedIntegratedDevice("aa",
                                 {u"设备串口号": "com2",
                                  u"空闲消息": u"欢迎光临\n天津滨海国际机场"})
    dv.showIdleMsgOnLed()
    time.sleep(5)
    dv.showOnLed(u"车牌 津A11111\n车型 1\n金额 0\n交易成功\n")

    dv.openAlarm(1)
    time.sleep(0.5)
    dv.closeAlarm(1)
# """
