#encoding:utf-8
'''
Created on 2016-11-23
停简单（海康）摄像头驱动
@author: kcht
'''
from ctypes import windll,c_char,c_int,byref
from PyQt4 import QtCore, QtGui
from shhicparking.infrastructure.AbstractInfrastructures import *

G_BSIM_DLL = windll.LoadLibrary("driver/libHKWrap.dll")
G_BSIM_DLL.initSDK()


class TjdCamera(AbstractInfrastructure,Camera,PhotoCapture,PlatePhotoParser):
    class VLCWidget(QtGui.QWidget):
        '''VLC播放Widget，其实真正的视频是播放在它的parent中'''
        vlcPath = None  #VLC路径
        def __init__(self,parent,param):
            QtGui.QWidget.__init__(self,parent)
            self.vedioUrl = param
            self.initVedio()
            
        def initVedio(self):
            import sys
            sys.path.append(TjdCamera.VLCWidget.vlcPath)
            import vlc
            self.vlc = vlc.Instance()
            self.player = self.vlc.media_player_new()
            hwnd = int(self.parent().winId())
            self.player.set_hwnd(hwnd)
            media = self.vlc.media_new(self.vedioUrl)
            self.player.set_media(media) 
            self.player.play()
        
    def __init__(self,infrasId, props):
        AbstractInfrastructure.__init__(self, infrasId, props)
        global G_BSIM_DLL
        self.dll = G_BSIM_DLL
        self.ip = str(props[u"设备IP"])
        port = int(props[u"端口号"])
        username = str(props[u"用户名"])
        password = str(props[u"密码"])
        TjdCamera.VLCWidget.vlcPath = str(props[u"VLC驱动路径"])
        self.vedioUrl = "rtsp://%s:%s@%s"%(username,password,self.ip)
        res = self.dll.startDevice(self.ip,port,username,password) 
        if res != 0:
            raise Exception(u"初始化摄像头失败")
        
    def startVedio(self,uiFrame):
        '''开始视频'''
        uiFrame.vedioFrameImplCls = TjdCamera.VLCWidget
        uiFrame.emit(QtCore.SIGNAL("INIT_VEDIO_FRAME(QString)"),self.vedioUrl)
        
    def stopVedio(self):
        '''结束视频'''
        self.player.stop()
        
    def capturePhoto(self):
        '''触发抓拍'''
        buf = (c_char*409600)()
        bufLen = c_int()
        plateBuf = (c_char*16)()
        res = self.dll.captureAndParseImage(self.ip,byref(buf),byref(bufLen),byref(plateBuf))
        if res == -1:
            self.parseResult = None
            return bytearray()
        elif res == 0:
            self.parseResult = plateBuf.value.decode("gb2312")
            return buf.raw[:bufLen.value]
        else:
            self.parseResult = None
            return buf.raw[:bufLen.value]    
    
    def parsePlateNo(self,photo=None):
        '''号牌识别，返回车牌和车型，入参可能是图片，也可能空（硬识别）'''
        if self.parseResult is not None:
            return self.parseResult[1:],u"小型车"
        return None,None
    
        
        
        
        