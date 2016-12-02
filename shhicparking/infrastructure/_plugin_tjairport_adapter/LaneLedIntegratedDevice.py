# encoding:utf-8
'''
Created on 2016-11-23
车道LED显示器
@author: kcht
'''
from kcht_complex_etc.infras import *
from shhicparking.infrastructure.AbstractInfrastructures import *


class LaneLedIntegratedDevice(AbstractInfrastructure, CETC_Alarm, LED):
    def __init__(self, infrasId, props):
        AbstractInfrastructure.__init__(self, infrasId, props)
        self.devicePort = props[u"设备串口号"]
        self.idleMessage = props[u"空闲消息"]

    def showOnLed(self, message):
        '''LED上显示消息'''

    def showIdleMsgOnLed(self):
        '''LED上显示默认空闲消息'''  # 可由子类重写，也可以不实现
        self.showOnLed(self.idleMessage)

    def openAlarm(self, alarmNo=0):
        "打开报警器"  # 入参可选，是报警器号

    def closeAlarm(self, alarmNo=0):
        "关闭报警器"  # 入参可选，是报警器号


if __name__ == '__main__':
    dv = LaneLedIntegratedDevice("aa", {u"设备串口号": "com1", u"空闲消息": "Hello World. 天津科畅慧通科技有限公司"})

    dv = LaneLedIntegratedDevice("aa", props)
