#encoding:utf-8
'''
Created on 2016-9-19
复杂高速ETC车道，入口逻辑
@author: zws
'''

from AbstractComplexEtcBiz import AbstractComplexEtcChannel,AbstractCetcState
import time


class ComplexEtcEntryBiz(AbstractComplexEtcChannel):
    class EnterIdleState(AbstractCetcState):
        "空闲状态"
        def entryStateBiz(self):
            self.infrasGroup["LED"].showOnLed(u"")
            self.infrasGroup["CETC_Alarm"].closeAlarm()
            self.infrasGroup["Guardrail"].dropTheRail()
            self.uiFrame.notifyActionInfras()
            self.uiFrame.notifyVehicleInfo()
            self.uiFrame.notifyVehicleOnCoil()
            self.uiFrame.notifySignals()
    
        def checkStateTrans(self):
            if self.infrasGroup["CETC_GroundCoils"].hasVehicle(1):
                self.uiFrame.notifyActionInfras(type="rsu",value="success")
            elif self.infrasGroup["CETC_GroundCoils"].hasVehicle(3):
                self.uiFrame.notifyActionInfras(type="rsu",value="fail")
            else:
                self.uiFrame.notifyActionInfras(type="rsu",value="idle")
                
            return None


    def __init__(self,infrasGroup,uiFrame):
        AbstractComplexEtcChannel.__init__(self,infrasGroup,uiFrame)
        self.currentState = ComplexEtcEntryBiz.EnterIdleState(self.infrasGroup,self.uiFrame,self.infoContainer)
        self.start()
        
    