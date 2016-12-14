#encoding:utf-8
'''
Created on 2016-9-19
复杂ETC车道基础逻辑
@author: zws
'''

from threading import Thread,RLock,Event
import logging
import time

from shhicparking import SESSION
from shhicparking.biz.InfoContainer import InfoContainer
from shhicparking.util import dateutil

class AbstractCetcState:
    "抽象车道状态，所有车道状态都从此类派生"
    def __init__(self,infrasGroup,uiFrame,infoContainer = None):
        self.infrasGroup = infrasGroup
        self.uiFrame = uiFrame
        self.infoContainer = infoContainer
        self.enterStateTime = 0 #进入本状态的时间(秒时间戳）
        self.STATE_TIMEOUT = -1 #状态超时时间（秒），如果超时，应当有处理。
    
    def entryStateBiz(self):
        "进入本状态时执行的逻辑"
        pass
    
    def doStateBiz(self):
        "状态下的执行逻辑，周期执行"
        #返回False表示逻辑执行失败，还需要下个周期继续执行，返回TRUE表示执行成功，就不再执行了
        pass
    
    def checkStateTrans(self):
        "检查状态转移"#无状态转移，返回None，有状态转移，返回那个状态类
        pass
    
    def exitStateBiz(self):
        "离开本状态时执行的逻辑"
        pass
    
    def bizOnTimeout(self):
        "超时时的业务逻辑，周期执行"
        pass

    def ifToIdle(self):
        gc = self.infrasGroup["CETC_GroundCoils"]
        for i in range(1,4):    
            if gc.hasVehicle(i):return False
        return True


class AbstractComplexEtcChannel(Thread):
    "车道逻辑，出入口车道逻辑从此类派生，本类包含状态机调度逻辑"
    def __init__(self,infrasGroup,uiFrame):
        Thread.__init__(self)
        self.shouldRunning = True
        self.infoContainer = InfoContainer(infrasGroup.infrasGroupId)    #过程信息容器
        self.uiFrame = uiFrame
        self.uiFrame.infoContainer = self.infoContainer #使界面能够访问信息容器
        self.infrasGroup = infrasGroup
        SESSION["%s-etcLaneMode"%infrasGroup.infrasGroupId] = "normal" #初始车道状态是普通状态

        #以下两个工具用于控制状态转移同步
        self.stateEvent = Event()
        self.currentState = AbstractCetcState(None,None,None)    #必须由子类注入初始状态
        self.vehicleCoilState = [False,False,False,False,False,False]

        self.photoCaptureThread = PhotoCaptureThread()  #抓拍识别线程
        self.photoCaptureThread.start()
        
    def run(self):
        self.infrasGroup["CETC_CanopyLights"].notifyNormal()    #车道逻辑还是运行，雨棚灯显示正常
        self.infrasGroup["Camera"].startVedio(self.uiFrame)
        while self.shouldRunning:
            try:
                self.currentState.entryStateBiz()
                finishDoBiz = False
                while True:
                    self.__showCoilToUi()
                    if not finishDoBiz: 
                        finishDoBiz = self.currentState.doStateBiz()
                    nextStateCls = self.currentState.checkStateTrans()
                    if nextStateCls is not None:    #有状态转移
                        self.currentState.exitStateBiz()
                        self.currentState = nextStateCls(self.infrasGroup,self.uiFrame,self.infoContainer)
                        self.currentState.photoCaptureThread = self.photoCaptureThread
                        self.currentState.enterStateTime = time.time()
                        print "---"*10,dateutil.nowStr(),'转入状态:',self.currentState.__class__.__name__,"---"*10
                        break
                    elif self.currentState.STATE_TIMEOUT != -1 and  \
                        time.time() - self.currentState.enterStateTime > self.currentState.STATE_TIMEOUT: #没有状态转移，但停留在这个状态下超时了
                        self.currentState.bizOnTimeout()
                    time.sleep(0.1)
            except Exception,e:
                import traceback
                exstr = traceback.format_exc()
                logging.getLogger().error(e)
                logging.getLogger().error(exstr)
        self.infrasGroup["Camera"].stopVedio(self.uiFrame)
        
    def notifyStop(self):
        '''停止线程'''
        self.shouldRunning = False
        logging.getLogger().info(u"拟移除基础设施组:%s"%self.infrasGroup.infrasGroupId)
        self.photoCaptureThread.stopThread()
        
    def __showCoilToUi(self):
        gc = self.infrasGroup["CETC_GroundCoils"]
        for i in range(3):
            if self.vehicleCoilState[i] != gc.hasVehicle(i+1):
                self.vehicleCoilState[i] = not self.vehicleCoilState[i]
                self.uiFrame.notifyVehicleOnCoil(coilNum = i+1,isVehicleOn = self.vehicleCoilState[i])


class PhotoCaptureThread(Thread):
    "视频抓拍识别线程"
    def __init__(self):
        Thread.__init__(self)
        self.shouldRunning = True
        self.captureEvent = Event()
        self.resultEvent = Event()
        self.photoCapture = None
        self.platePhotoParser = None
        self.result = [None,None,None]  #三个结果：图片，车牌号，车型
   
    def triggerCaptureAndParse(self,photoCapture,platePhotoParser = None):
        self.photoCapture = photoCapture
        self.platePhotoParser = platePhotoParser if platePhotoParser is not None else photoCapture
        self.captureEvent.set()
    
    def getCaptureAndParseResult(self):
        self.resultEvent.wait(3)
        self.resultEvent.clear()
        return self.result[0],self.result[1],self.result[2]
    
    def run(self):
        while self.shouldRunning:
            try:
                self.captureEvent.wait()
                self.captureEvent.clear()
                self.result = [None,None,None]
                self.result[0] = self.photoCapture.capturePhoto()
                self.result[1],self.result[2] = self.platePhotoParser.parsePlateNo(self.result[0])
            finally:
                self.resultEvent.set()
        
    def stopThread(self):    
        self.shouldRunning = False
















