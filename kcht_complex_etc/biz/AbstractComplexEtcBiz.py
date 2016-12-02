#encoding:utf-8
'''
Created on 2016-9-19
复杂ETC车道基础逻辑
@author: zws
'''

from threading import Thread,RLock,Event
import logging
import time


class AbstractCetcState:
    def __init__(self,infrasGroup,uiFrame,infoContainer = None):
        self.infrasGroup = infrasGroup
        self.uiFrame = uiFrame
        self.infoContainer = infoContainer
    
    def entryStateBiz(self):
        "进入本状态时执行的逻辑"
        pass
    
    def doStateBiz(self):
        "状态下的执行逻辑，周期执行"
        pass
    
    def checkStateTrans(self):
        "检查状态转移"#无状态转移，返回None，有状态转移，返回那个状态类
        pass
    
    def exitStateBiz(self):
        "离开本状态时执行的逻辑"
        pass

    def ifToIdle(self):
        gc = self.infrasGroup["CETC_GroundCoils"]
        for i in range(1,7):    #旁道误入报警
            if gc.hasVehicle(i):return False
        return True


class AbstractComplexEtcChannel(Thread):
    def __init__(self,infrasGroup,uiFrame):
        Thread.__init__(self)
        self.shouldRunning = True
        self.infoContainer = None    #过程信息容器
        self.uiFrame = uiFrame
        self.uiFrame.infoContainer = self.infoContainer #使界面能够访问信息容器
        self.infrasGroup = infrasGroup

                
        #以下两个工具用于控制状态转移同步
        self.stateEvent = Event()
        self.currentState = AbstractCetcState(None,None,None)    #必须由子类注入初始状态
        self.vehicleCoilState = [False,False,False,False,False,False]
        
        
    def run(self):
        while self.shouldRunning:
            try:
                self.currentState.entryStateBiz()
                while True:
                    self.__showCoilToUi()
                    self.currentState.doStateBiz()
                    nextStateCls = self.currentState.checkStateTrans()
                    if nextStateCls is not None:
                        self.currentState.exitStateBiz()
                        self.currentState = nextStateCls(self.infrasGroup,self.uiFrame,self.infoContainer)
                        print '转入状态:',self.currentState.__class__.__name__
                        break
            except Exception,e:
                import traceback
                exstr = traceback.format_exc()
                logging.getLogger().error(e)
                logging.getLogger().error(exstr)
        
    def notifyStop(self):
        '''停止线程'''
        self.shouldRunning = False
        logging.getLogger().info(u"拟移除基础设施组:%s"%self.infrasGroup.infrasGroupId)
        
    def __showCoilToUi(self):
        gc = self.infrasGroup["CETC_GroundCoils"]
        for i in range(3):
            if self.vehicleCoilState[i] != gc.hasVehicle(i+1):
                self.vehicleCoilState[i] = not self.vehicleCoilState[i]
                self.uiFrame.notifyVehicleOnCoil(coilNum = i+1,isVehicleOn = self.vehicleCoilState[i])























