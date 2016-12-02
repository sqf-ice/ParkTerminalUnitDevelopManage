#encoding:utf-8
'''
Created on 2016-9-19
复杂高速ETC车道，入口逻辑
@author: zws
'''

from AbstractComplexEtcBiz import AbstractComplexEtcChannel,AbstractCetcState
from shhicparking import PARAM
import time


class ComplexEtcEntryBiz(AbstractComplexEtcChannel):
    class EnterIdleState(AbstractCetcState):
        "空闲状态"
        def entryStateBiz(self):
            self.infrasGroup["LED"].showOnLed(PARAM["idleEntryLedMessage"])
            self.infrasGroup["CETC_Alarm"].closeAlarm()
            self.infrasGroup["Guardrail"].dropTheRail()
            self.uiFrame.notifyActionInfras()
            self.uiFrame.notifyVehicleInfo()
            self.uiFrame.notifyVehicleOnCoil()
            self.uiFrame.notifySignals()
    
        def checkStateTrans(self):
            gc = self.infrasGroup["CETC_GroundCoils"]
            if len(filter(lambda g:gc.hasVehicle(g),range(2,7))) != 0:  #旁道误入报警
                return ComplexEtcEntryBiz.WronglyEntryWarningState
            if gc.hasVehicle(1):#一线圈触发
                return ComplexEtcEntryBiz.FirstVehicleTradingState

    class WronglyEntryWarningState(AbstractCetcState):
        "误入报警状态"
        def entryStateBiz(self):
            self.infrasGroup["CETC_Alarm"].openAlarm()
            self.uiFrame.notifySignals(type="alarm",value="alarm")
            self.uiFrame.notifySignals(type="pass",value="alarm")
    
        def checkStateTrans(self):
            return ComplexEtcEntryBiz.EnterIdleState if self.ifToIdle() else None
    
    class FirstVehicleTradingState(AbstractCetcState):
        "第一车交易中状态"
        def __init__(self,infrasGroup,uiFrame,infoContainer):
            AbstractCetcState.__init__(self,infrasGroup,uiFrame,infoContainer)
            self.tradeSucc = None
        
        def entryStateBiz(self):
            self.uiFrame.notifyActionInfras(type="rsu",value="acting")
        
        def doStateBiz(self):
            #TODO 触发RSU交易，交易成功则置标志位self.tradeSucc
            pass

        def exitStateBiz(self):
            self.uiFrame.notifyActionInfras(type="rsu",value="success" if self.tradeSucc else "fail")
            
        def checkStateTrans(self):
            if self.ifToIdle():return ComplexEtcEntryBiz.EnterIdleState #车道空闲，转移到空闲状态
            if self.tradeSucc:return ComplexEtcEntryBiz.FirstVehicleTradingSucceedState #交易成功，直接转移到第一车交易成功状态
            elif self.infrasGroup["CETC_GroundCoils"].hasVehicle(3):#交易未成功，但三线圈触发了，转入第一车交易失败状态
                return ComplexEtcEntryBiz.FirstVehicleTradingFailState
        
    class FirstVehicleTradingSucceedState(AbstractCetcState):
        "第一车交易成功"
        def entryStateBiz(self):
            self.infrasGroup["LED"].showOnLed(u"TODO 交易成功，放行")
            self.infrasGroup["Guardrail"].liftTheRail()
            #TODO 记录数据
            
        def checkStateTrans(self):
            if self.ifToIdle():return ComplexEtcEntryBiz.EnterIdleState #车道空闲，转移到空闲状态
            if self.infrasGroup["CETC_GroundCoils"].hasVehicle(4) or self.infrasGroup["CETC_GroundCoils"].hasVehicle(5):
                #四、五线圈触发，转移到等待新交易触发的状态
                return ComplexEtcEntryBiz.WaitForNewTradeState
            
        def exitStateBiz(self):
            self.uiFrame.notifyActionInfras(type="rsu",value="idle")
            
        
    class WaitForNewTradeState(AbstractCetcState):
        "等待新交易触发"
        def checkStateTrans(self):
            if self.ifToIdle():return ComplexEtcEntryBiz.EnterIdleState #车道空闲，转移到空闲状态
            if self.infrasGroup["CETC_GroundCoils"].hasVehicle(1) or self.infrasGroup["CETC_GroundCoils"].hasVehicle(2):
                return ComplexEtcEntryBiz.FirstVehicleTradingState
        
        def exitStateBiz(self):
            self.uiFrame.notifyActionInfras(type="bar",value="idle")
                
        
    class FirstVehicleTradingFailState(AbstractCetcState):
        "第一车交易失败"
        def __init__(self, infrasGroup, uiFrame, infoContainer=None):
            AbstractCetcState.__init__(self, infrasGroup, uiFrame, infoContainer=infoContainer)
            self.tradeFailTime = time.time()    #RSU交易失败时间，用于等待超时不取卡的情况
            self.hasTakeTicket = None  #是否已取票
                
        def entryStateBiz(self):
            self.infrasGroup["LED"].showOnLed(u"TODO 提示交易失败，取票")
            self.uiFrame.notifyActionInfras(type="ic",value="acting")
            
        def checkStateTrans(self):
            if self.ifToIdle():return ComplexEtcEntryBiz.EnterIdleState #车道空闲，转移到空闲状态
            if self.hasTakeTicket:  #已取票，进入普票后待入场状态
                return ComplexEtcEntryBiz.TakeTicketEntryState
            elif time.time() - self.tradeFailTime > 120 or \
                self.infrasGroup["CETC_GroundCoils"].hasVehicle(5):  
                #超过两分钟不取票，就甭取了，进入不可入报警状态
                #不取票车往前走了，也报警
                return ComplexEtcEntryBiz.CanNotEntryState
        
    class TakeTicketEntryState(AbstractCetcState):
        "取票后待入场"
        def entryStateBiz(self):
            self.infrasGroup["LED"].showOnLed(u"TODO 已取票，请入场")
            self.infrasGroup["Guardrail"].liftTheRail()
            self.uiFrame.notifyActionInfras(type="ic",value="success")
            self.uiFrame.notifyActionInfras(type="rsu",value="idle")

        def checkStateTrans(self):
            if self.ifToIdle():return ComplexEtcEntryBiz.EnterIdleState #车道空闲，转移到空闲状态
            if self.infrasGroup["CETC_GroundCoils"].hasVehicle(4) or self.infrasGroup["CETC_GroundCoils"].hasVehicle(5):
                #四、五线圈触发，转移到等待新交易触发的状态
                return ComplexEtcEntryBiz.WaitForNewTradeState
            
                        
    class CanNotEntryState(AbstractCetcState):
        "不可入场状态"
        def entryStateBiz(self):
            self.infrasGroup["CETC_Alarm"].openAlarm()
            self.uiFrame.notifySignals(type="alarm",value="alarm")
            self.uiFrame.notifySignals(type="pass",value="alarm")
            
        def checkStateTrans(self):
            if self.ifToIdle():return ComplexEtcEntryBiz.EnterIdleState #车道空闲，转移到空闲状态
    
    def __init__(self,infrasGroup,uiFrame):
        AbstractComplexEtcChannel.__init__(self,infrasGroup,uiFrame)
        self.currentState = ComplexEtcEntryBiz.EnterIdleState(self.infrasGroup,self.uiFrame,self.infoContainer)
        self.start()
        
    