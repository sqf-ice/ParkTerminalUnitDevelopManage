# encoding:utf-8
'''
Created on 2017-2-7
泊享地锁，结合串口服务器实现
@author: kcht
'''

from SerialServer import fetchSerialServer
import time


class GroundLock:
    # 地锁设备
    STATE_UNKNOWN = -1
    STATE_OPEN = 1
    STATE_CLOSE = 2
    SET_ULTRA_CHECK_SUCCESS = 4
    GET_ULTRA_CHECK_SUCCESS = 5
    SET_ULTRA_FILTER_SUCCESS = 6
    GET_ULTRA_FILTER_SUCCESS = 7
    GET_ULTRA_PARAS_SUCCESS = 8
    SET_BUZZER_SUCCESS = 9
    GET_VERSION_SUCCESS = 10
    SET_ULTRA_SWITCH_SUCCESS = 11
    SET_ADDR_SUCCESS = 12
    GET_ADDR_SUCCESS = 13
    SET_BAUD_SUCCESS = 14
    GET_MAC_SUCCESS = 15

    # 开锁
    def openLock(self):
        raise Exception("No implement for GroundLock")

    # 闭锁
    def closeLock(self):
        raise Exception("No implement for GroundLock")

    # 读取锁状态
    def getLockState(self):
        raise Exception("No implement for GroundLock")

    # 设置超声波检测周期
    def setUltraSoundCheck(self):
        raise Exception("No implement for GroundLock")

    # 读超声波检测周期
    def getUltraSoundCheck(self):
        raise Exception("No implement for GroundLock")

    # 设置超声波滤波时间
    def setUltraSoundFilter(self):
        raise Exception("No implement for GroundLock")

    # 读取超声波滤波时间
    def getUltraSoundFilter(self):
        raise Exception("No implement for GroundLock")

    # 超声波运行参数查询
    def getUltraSoundParams(self):
        raise Exception("No implement for GroundLock")

    # 蜂鸣器输出设置/查询
    def setBuzzer(self):
        raise Exception("No implement for GroundLock")

    # 软硬件版本号读取
    def getVersion(self):
        raise Exception("No implement for GroundLock")

    # 设置超声波探测开关/查询
    def setUltraSoundSwitch(self):
        raise Exception("No implement for GroundLock")

    # ADDR 设置
    def setAddr(self):
        raise Exception("No implement for GroundLock")

    # ADDR 查询
    def getAddr(self):
        raise Exception("No implement for GroundLock")

    # 波特率设置
    def setBaud(self):
        raise Exception("No implement for GroundLock")

    # 网络 MAC 地址查询
    def getMAC(self):
        raise Exception("No implement for GroundLock")


class BXGroundLock(GroundLock):
    def __init__(self, ip, port, serialAddr):
        self.serialAddr = serialAddr
        self.ss = fetchSerialServer(ip, port)

    def __checkResponseCrc(self, res):
        # 校验返回帧的CRC
        if res[0] != 0x5a: return False  # 校验帧头
        if CRC8_Tab(res[2:5]) != res[5]: return False  # 校验CRC
        return True

    def __checkResponseDataCrc(self, res):
        # 校验返回帧的CRC
        if res[0] != 0x5a: return False  # 校验带数据的帧头
        if CRC8_Tab(res[2:6]) != res[6]: return False  # 校验CRC
        return True

    def __checkResponseMacCrc(self, res):
        # 校验返回帧的CRC
        if res[0] != 0x5a: return False  # 校验带数据的帧头
        if CRC8_Tab(res[2:10]) != res[10]: return False  # 校验CRC
        return True

    def openLock(self):
        cmd = [0x55, self.serialAddr, 0x01, 0x01, None, 0xaa]
        cmd[4] = CRC8_Tab(cmd[2:4])
        try:
            res = self.ss.sendAndRecv(cmd)
            return GroundLock.STATE_UNKNOWN if not self.__checkResponseCrc(res) else GroundLock.STATE_OPEN
        except Exception, e:
            print e
            return GroundLock.STATE_UNKNOWN

    def closeLock(self):
        cmd = [0x55, self.serialAddr, 0x01, 0x02, None, 0xaa]
        cmd[4] = CRC8_Tab(cmd[2:4])
        try:
            res = self.ss.sendAndRecv(cmd)
            return GroundLock.STATE_UNKNOWN if not self.__checkResponseCrc(res) else GroundLock.STATE_CLOSE
        except Exception, e:
            print e
            return GroundLock.STATE_UNKNOWN

    def getLockState(self):
        crc = None
        cmd = [0x55, self.serialAddr, 0x01, 0x06, None, 0xaa]
        cmd[4] = CRC8_Tab(cmd[2:4])
        try:
            res = self.ss.sendAndRecv(cmd)
            if not self.__checkResponseCrc(res): return GroundLock.STATE_UNKNOWN
            if res[4] == 0x00:
                return GroundLock.STATE_CLOSE
            elif res[4] == 0x01:
                return GroundLock.STATE_OPEN
        except Exception, e:
            print e
            return GroundLock.STATE_UNKNOWN

    def setUltraSoundCheck(self):
        cmd = [0x55, self.serialAddr, 0x02, 0x07, 0x01, None, 0xaa]
        cmd[5] = CRC8_Tab(cmd[2:5])
        try:
            res = self.ss.sendAndRecv(cmd)
            return GroundLock.STATE_UNKNOWN if not self.__checkResponseCrc(res) else GroundLock.SET_ULTRA_CHECK_SUCCESS
        except Exception, e:
            print e
            return GroundLock.STATE_UNKNOWN

    def getUltraSoundCheck(self):
        cmd = [0x55, self.serialAddr, 0x01, 0x08, None, 0xaa]
        cmd[4] = CRC8_Tab(cmd[2:4])
        try:
            res = self.ss.sendAndRecv(cmd)
            return GroundLock.STATE_UNKNOWN if not self.__checkResponseCrc(res) else res[4]
        except Exception, e:
            print e
            return GroundLock.STATE_UNKNOWN

    def setUltraSoundFilter(self):
        cmd = [0x55, self.serialAddr, 0x02, 0x09, 0x01, None, 0xaa]
        cmd[5] = CRC8_Tab(cmd[2:5])
        try:
            res = self.ss.sendAndRecv(cmd)
            return GroundLock.STATE_UNKNOWN if not self.__checkResponseCrc(res) \
                else GroundLock.SET_ULTRA_FILTER_SUCCESS
        except Exception, e:
            print e
            return GroundLock.STATE_UNKNOWN

    def getUltraSoundFilter(self):
        cmd = [0x55, self.serialAddr, 0x01, 0x0a, None, 0xaa]
        cmd[4] = CRC8_Tab(cmd[2:4])
        try:
            res = self.ss.sendAndRecv(cmd)
            return GroundLock.STATE_UNKNOWN if not self.__checkResponseCrc(res) else res[4]
        except Exception, e:
            print e
            return GroundLock.STATE_UNKNOWN

    def getUltraSoundParams(self):
        cmd = [0x55, self.serialAddr, 0x01, 0x14, None, 0xaa]
        cmd[4] = CRC8_Tab(cmd[2:4])
        try:
            res = self.ss.sendAndRecv(cmd)
            return GroundLock.STATE_UNKNOWN if not self.__checkResponseDataCrc(res) else res[4:6]
        except Exception, e:
            print e
            return GroundLock.STATE_UNKNOWN

    def setBuzzer(self, data):
        cmd = [0x55, self.serialAddr, 0x02, 0x15, data, None, 0xaa]
        cmd[5] = CRC8_Tab(cmd[2:5])
        try:
            res = self.ss.sendAndRecv(cmd)
            if data == 02:  # 查询
                return GroundLock.STATE_UNKNOWN if not self.__checkResponseCrc(res) else res[4]
            else:  # 设置
                return GroundLock.STATE_UNKNOWN if not self.__checkResponseCrc(res) else GroundLock.SET_BUZZER_SUCCESS
        except Exception, e:
            print e
            return GroundLock.STATE_UNKNOWN

    def getVersion(self):
        cmd = [0x55, self.serialAddr, 0x01, 0x1a, 0x27, 0xaa]
        try:
            res = self.ss.sendAndRecv(cmd)
            return GroundLock.STATE_UNKNOWN if not self.__checkResponseDataCrc(res) else res[4:6]
        except Exception, e:
            print e
            return GroundLock.STATE_UNKNOWN

    def setUltraSoundSwitch(self, data):
        cmd = [0x55, self.serialAddr, 0x02, 0x1b, data, None, 0xaa]
        cmd[5] = CRC8_Tab(cmd[2:5])
        try:
            res = self.ss.sendAndRecv(cmd)
            if data == 02:  # 查询
                return GroundLock.STATE_UNKNOWN if not self.__checkResponseCrc(res) else res[4]
            else:  # 设置
                return GroundLock.STATE_UNKNOWN if not self.__checkResponseCrc(res) \
                    else GroundLock.SET_ULTRA_SWITCH_SUCCESS
        except Exception, e:
            print e
            return GroundLock.STATE_UNKNOWN

    def setAddr(self, data):
        cmd = [0x55, self.serialAddr, 0x02, 0x1c, data, None, 0xaa]
        cmd[5] = CRC8_Tab(cmd[2:5])
        try:
            res = self.ss.sendAndRecv(cmd)
            return GroundLock.STATE_UNKNOWN if not self.__checkResponseCrc(res) \
                else GroundLock.SET_ADDR_SUCCESS
        except Exception, e:
            print e
            return GroundLock.STATE_UNKNOWN

    def getAddr(self):
        cmd = [0x55, 0xff, 0x01, 0x1d, 0xa4, 0xaa]
        try:
            res = self.ss.sendAndRecv(cmd)
            return GroundLock.STATE_UNKNOWN if not self.__checkResponseCrc(res) else res[4]
        except Exception, e:
            print e
            return GroundLock.STATE_UNKNOWN

    def setBaud(self, data):
        cmd = [0x55, self.serialAddr, 0x02, 0x1e, data, None, 0xaa]
        cmd[5] = CRC8_Tab(cmd[2:5])
        try:
            res = self.ss.sendAndRecv(cmd)
            return GroundLock.STATE_UNKNOWN if not self.__checkResponseCrc(res) else GroundLock.SET_BAUD_SUCCESS
        except Exception, e:
            print e
            return GroundLock.STATE_UNKNOWN

    def getMAC(self):
        cmd = [0x55, self.serialAddr, 0x01, 0x22, None, 0xaa]
        cmd[4] = CRC8_Tab(cmd[2:4])
        try:
            res = self.ss.sendAndRecv(cmd)
            return GroundLock.STATE_UNKNOWN if not self.__checkResponseMacCrc(res) \
                else res[4:10]
        except Exception, e:
            print e
            return GroundLock.STATE_UNKNOWN


CRC8_TAB = [0x00, 0x5e, 0xbc, 0xe2, 0x61, 0x3f, 0xdd, 0x83,
            0xc2, 0x9c, 0x7e, 0x20, 0xa3, 0xfd, 0x1f, 0x41,
            0x9d, 0xc3, 0x21, 0x7f, 0xfc, 0xa2, 0x40, 0x1e,
            0x5f, 0x01, 0xe3, 0xbd, 0x3e, 0x60, 0x82, 0xdc,
            0x23, 0x7d, 0x9f, 0xc1, 0x42, 0x1c, 0xfe, 0xa0,
            0xe1, 0xbf, 0x5d, 0x03, 0x80, 0xde, 0x3c, 0x62,
            0xbe, 0xe0, 0x02, 0x5c, 0xdf, 0x81, 0x63, 0x3d,
            0x7c, 0x22, 0xc0, 0x9e, 0x1d, 0x43, 0xa1, 0xff,
            0x46, 0x18, 0xfa, 0xa4, 0x27, 0x79, 0x9b, 0xc5,
            0x84, 0xda, 0x38, 0x66, 0xe5, 0xbb, 0x59, 0x07,
            0xdb, 0x85, 0x67, 0x39, 0xba, 0xe4, 0x06, 0x58,
            0x19, 0x47, 0xa5, 0xfb, 0x78, 0x26, 0xc4, 0x9a,
            0x65, 0x3b, 0xd9, 0x87, 0x04, 0x5a, 0xb8, 0xe6,
            0xa7, 0xf9, 0x1b, 0x45, 0xc6, 0x98, 0x7a, 0x24,
            0xf8, 0xa6, 0x44, 0x1a, 0x99, 0xc7, 0x25, 0x7b,
            0x3a, 0x64, 0x86, 0xd8, 0x5b, 0x05, 0xe7, 0xb9,
            0x8c, 0xd2, 0x30, 0x6e, 0xed, 0xb3, 0x51, 0x0f,
            0x4e, 0x10, 0xf2, 0xac, 0x2f, 0x71, 0x93, 0xcd,
            0x11, 0x4f, 0xad, 0xf3, 0x70, 0x2e, 0xcc, 0x92,
            0xd3, 0x8d, 0x6f, 0x31, 0xb2, 0xec, 0x0e, 0x50,
            0xaf, 0xf1, 0x13, 0x4d, 0xce, 0x90, 0x72, 0x2c,
            0x6d, 0x33, 0xd1, 0x8f, 0x0c, 0x52, 0xb0, 0xee,
            0x32, 0x6c, 0x8e, 0xd0, 0x53, 0x0d, 0xef, 0xb1,
            0xf0, 0xae, 0x4c, 0x12, 0x91, 0xcf, 0x2d, 0x73,
            0xca, 0x94, 0x76, 0x28, 0xab, 0xf5, 0x17, 0x49,
            0x08, 0x56, 0xb4, 0xea, 0x69, 0x37, 0xd5, 0x8b,
            0x57, 0x09, 0xeb, 0xb5, 0x36, 0x68, 0x8a, 0xd4,
            0x95, 0xcb, 0x29, 0x77, 0xf4, 0xaa, 0x48, 0x16,
            0xe9, 0xb7, 0x55, 0x0b, 0x88, 0xd6, 0x34, 0x6a,
            0x2b, 0x75, 0x97, 0xc9, 0x4a, 0x14, 0xf6, 0xa8,
            0x74, 0x2a, 0xc8, 0x96, 0x15, 0x4b, 0xa9, 0xf7,
            0xb6, 0xe8, 0x0a, 0x54, 0xd7, 0x89, 0x6b, 0x35]


def CRC8_Tab(ptr, precrc=0x00):
    crc8 = precrc
    for i in range(len(ptr)):
        crc8 = CRC8_TAB[crc8 ^ (ptr[i])]
    return crc8


if __name__ == '__main__':

    gl1 = BXGroundLock("192.168.0.7", 8234, 1)
    gl4 = BXGroundLock("192.168.0.7", 8234, 4)


    def testCommunication():
        for i in range(3):
            gl1.openLock()
            gl4.closeLock()
            gl1.closeLock()
            gl4.openLock()


    def test():

        print "4.设置超声波检测周期-----------------------"
        print gl1.setUltraSoundCheck()
        time.sleep(1)

        print "5.读超声波检测周期-----------------------"
        print gl1.getUltraSoundCheck()
        time.sleep(1)

        print "6.设置超声波滤波时间-----------------------"
        print gl1.setUltraSoundFilter()
        time.sleep(1)

        print "7.读取超声波滤波时间-----------------------"
        print gl1.getUltraSoundFilter()
        time.sleep(1)

        print "8.超声波运行参数查询-----------------------"
        print gl1.getUltraSoundParams()
        time.sleep(1)

        print "9.蜂鸣器输出设置/查询-----------------------"
        print "00—蜂鸣器不输出，01—蜂鸣器输出,02—蜂鸣器输出查询"
        print gl1.setBuzzer(02)
        time.sleep(1)
        print gl1.setBuzzer(00)
        time.sleep(1)

        print "10.软硬件版本号读取-----------------------"
        print gl1.getVersion()
        time.sleep(1)

        print "11.设置超声波探测开关/查询-----------------------"
        print "00—打开，01—关闭，02—查询"
        print gl1.setUltraSoundSwitch(02)
        time.sleep(1)

        print "12.ADDR 设置-----------------------"
        print gl1.setAddr(0x01)
        time.sleep(1)

        print "13.ADDR 查询-----------------------"
        # print gl1.getAddr()
        print gl4.getAddr()
        time.sleep(1)

        print "14.波特率设置-----------------------"
        print "波特率 bps 0--9600,1--4800,2--2400,3--1200，4—600"
        print gl1.setBaud(0x00)
        time.sleep(1)

        print "15.网络 MAC 地址查询-----------------------"
        print gl1.getMAC()
        time.sleep(1)


    print "0.测试-----------------------"
    # testCommunication()
    time.sleep(1)

    print "1.开锁-----------------------"
    print gl1.openLock()
    print gl4.closeLock()
    time.sleep(1)

    print "2.闭锁-----------------------"
    print gl1.closeLock()
    print gl4.openLock()
    time.sleep(1)

    print "3.读取锁状态-----------------------"
    print gl1.getLockState()
    print gl4.getLockState()
    time.sleep(1)

    print "9.蜂鸣器输出设置/查询-----------------------"
    print "00—蜂鸣器不输出，01—蜂鸣器输出,02—蜂鸣器输出查询"
    print gl1.setBuzzer(01)
    print gl1.openLock()
    time.sleep(10)
    print gl1.closeLock()
    time.sleep(1)
    print gl1.setBuzzer(00)
    time.sleep(1)
    for i in range(0, 10):
        print "1.开锁1-----------------------闭锁4"
        print gl1.openLock()
        print gl4.closeLock()
        time.sleep(1)
        print "2.锁1状态----------------------锁4状态"
        print gl1.getLockState()
        print gl4.getLockState()
        time.sleep(1)
        print "3.闭锁4-----------------------开锁4"
        print gl1.closeLock()
        print gl4.openLock()
        time.sleep(1)
        print "4.锁1状态----------------------锁4状态"
        print gl1.getLockState()
        print gl4.getLockState()
        time.sleep(1)
