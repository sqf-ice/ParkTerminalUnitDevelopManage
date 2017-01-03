# encoding: utf-8


"""
@version: 1.0
@time: 2016/12/20 15:28
"""
import ctypes
import os
import sqlite3
import time
from _ctypes import byref
from threading import Thread

from kcht_complex_etc.infras import CTEC_DataHelper
from shhicparking.infrastructure.AbstractInfrastructures import *


class ResendThread(Thread):
    """检查数据库的内容，如果有纪录则重传"""

    def __init__(self, dll_path, db_path):
        Thread.__init__(self)
        try:
            self.conn = sqlite3.connect(db_path + '.db', check_same_thread=False)
        except Exception, e:
            print "数据库打开失败:" + str(e)
        try:
            self.dllUpload = ctypes.cdll.LoadLibrary(dll_path + 'KchtEtcParkClientHelper.dll')
        except Exception, e:
            print "KchtEtcParkClientHelper.dll初始化失败: " + str(e)

    def __loadFromDb(self):
        """查询数据库是否有内容"""
        cur = self.conn.execute("SELECT * FROM payload_json;")
        if cur.fetchone() is None:
            return None
        else:
            return self.conn.execute("SELECT * FROM payload_json;")

    def __resendRecord(self, cord):
        """"调用dll进行重传"""
        for row in cord:
            try:
                rtn = self.dllUpload.KTSV_resendNotify(row[0])
            except Exception, e:
                rtn = None
                print "DataUpload.__resendRecord.KTSV_resendNotify异常: " + str(e)
            finally:
                if rtn is 0:
                    self.conn.execute("DELETE FROM payload_json WHERE JSON= ?;", (row[0],))
                    self.conn.commit()

    def run(self):
        """轮询数据库"""
        while True:
            try:
                hasCord = self.__loadFromDb()
                if hasCord is not None:
                    self.__resendRecord(hasCord)
                else:
                    time.sleep(10)
                    continue

            except Exception, e:
                print "ResendThread异常: " + str(e)


class DataUpload(AbstractInfrastructure, CTEC_DataHelper):
    def __init__(self, infrasId, props):
        AbstractInfrastructure.__init__(self, infrasId, props)
        "KchtEtcParkClientHelper.dll初始化"
        try:
            dll_path = os.path.join(os.path.dirname(__file__) + '/../../../driver/')
            self.dllUpload = ctypes.cdll.LoadLibrary(dll_path + 'KchtEtcParkClientHelper.dll')
        except Exception, e:
            print "KchtEtcParkClientHelper.dll初始化失败: " + str(e)
        "新建数据库"
        db_path = os.path.join(os.path.dirname(__file__) + '/../../../logs/park-slot-sqlite')
        try:
            self.conn = sqlite3.connect(db_path + '.db', check_same_thread=False)
            self.conn.execute("CREATE TABLE IF NOT EXISTS payload_json (JSON TEXT, UPLOAD_TIME TEXT);")
        except Exception, e:
            print "数据库打开失败:" + str(e)
        "开启线程检测数据库纪录"
        self.resendThread = ResendThread(dll_path, db_path)
        self.resendThread.start()

    def __saveToBuffer(self, payloadJson):
        """save payloadJson to local database"""
        try:
            self.conn.execute("INSERT INTO payload_json VALUES (?, ?);", (str(payloadJson), time.time() * 1000))
            self.conn.commit()
        except Exception, e:
            print "DataUpload.__saveToBuffer异常: " + str(e)

    def notifyEntry(self, vehicleInfo=None, entryTradeResult=None):
        """入场上报服务"""
        payloadJson = ctypes.create_string_buffer(2048)
        try:
            rtn = self.dllUpload.KTSV_notifyEntry(vehicleInfo, entryTradeResult, byref(payloadJson))
        except Exception, e:
            rtn = None
            print "DataUpload.notifyExit.KTSV_notifyEntry异常: " + str(e)
        finally:
            if rtn is not 0:
                self.__saveToBuffer(payloadJson)

    def notifyExit(self, vehicleInfo=None, dueToll=None, exitTradeResult=None):
        """出场上报服务"""
        payloadJson = ctypes.create_string_buffer(2048)
        try:
            rtn = self.dllUpload.KTSV_notifyExit(vehicleInfo, dueToll, exitTradeResult, byref(payloadJson))
        except Exception, e:
            rtn = None
            print "DataUpload.notifyExit.KTSV_notifyExit异常: " + str(e)
        finally:
            if rtn is not 0:
                self.__saveToBuffer(payloadJson)


"""
if __name__ == '__main__':
    props = {u"触发线圈输入端子": 1, u"存在线圈输入端子": 2, u"停止线圈输入端子": 3,
             u"雨棚灯控制端子": 1, u"道闸抬起控制端子": 2, u"道闸落下控制端子": 3}
    DataUpload("bb", props).notifyEntry()
    # du.notifyEntry()
    # du.notifyExit()
    pass
"""
