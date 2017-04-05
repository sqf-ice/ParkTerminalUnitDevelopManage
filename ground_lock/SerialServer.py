# encoding:utf-8
'''
Created on 2017-2-7
串口服务器驱动
其实就是一个Socket，但是只是短连接实现
@author: kcht
'''
import socket
from threading import RLock
import time

serialServerPool = {}  # 串口服务器池，一个IP一个对象


class SerialServer:
    "串口服务器对象"  # 放入serialServerPool中

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.con = None
        self.lock = RLock()

    def createConnect(self):
        try:
            if self.con is None:
                con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                con.settimeout(5)
                con.connect((self.ip, self.port))
                self.con = con
        except Exception as e:
            raise e

    def closeConnection(self):
        try:
            if self.con is not None:
                self.con.close()
        finally:
            self.con = None

    def sendCmd(self, cmd):
        self.con.sendall(bytearray(cmd))

    def recv(self, bufSize=128):
        res = self.con.recv(bufSize)
        return [int(ord(i)) for i in res]

    def immediateSend(self, cmd):
        self.createConnect()
        self.sendCmd(cmd)
        self.closeConnection()

    def sendAndRecv(self, cmd):
        try:
            self.lock.acquire()
            self.createConnect()
            print "->", " ".join(["%.2x" % x for x in cmd])
            self.sendCmd(cmd)
            res = self.recv()
            print "<-", " ".join(["%.2x" % x for x in res])
            return res
        finally:
            try:
                self.closeConnection()
            finally:
                time.sleep(1)
                self.lock.release()


def fetchSerialServer(ip, port):
    "获取一个串口服务器对象"
    if ip not in serialServerPool:
        serialServerPool[ip] = SerialServer(ip, port)
    return serialServerPool[ip]
