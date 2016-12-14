#encoding:utf-8
'''
Created on 2016-9-19
复杂高速ETC车道，入口逻辑
@author: zws
'''

from AbstractComplexEtcBiz import AbstractComplexEtcChannel,AbstractCetcState
from kcht_complex_etc.infras import FrontendEtc
import time
from shhicparking.util import dateutil
from shhicparking import SESSION
from shhicparking.server import TSStub

class ComplexEtcEntryBiz(AbstractComplexEtcChannel):
    class EnterIdleState(AbstractCetcState):
        "空闲状态"
        def entryStateBiz(self):
            self.infoContainer.finish()
            self.uiFrame.notifyActionInfras()
            self.uiFrame.notifyVehicleInfo()
            self.uiFrame.notifyVehicleOnCoil()
            self.uiFrame.notifySignals()
            self.infrasGroup["CETC_Alarm"].closeAlarm()
            self.infrasGroup["LED"].showIdleMsgOnLed()
            self.infrasGroup["Guardrail"].dropTheRail()
        
        def checkStateTrans(self):
            gc = self.infrasGroup["CETC_GroundCoils"]
            if gc.hasVehicle(2) or gc.hasVehicle(3):
                return ComplexEtcEntryBiz.UnexceptedEnterState
            if gc.hasVehicle(1):#一线圈触发
                return ComplexEtcEntryBiz.FirstTradingState
    
    class UnexceptedEnterState(AbstractCetcState):
        "旁道误入告警状态"
        def entryStateBiz(self):
            SESSION["mainWnd"].log(msg = u"错误：车辆旁道误入")
            self.infrasGroup["LED"].showOnLed(u"旁道误入\n请退出车道重入")
            self.infrasGroup["CETC_Alarm"].openAlarm()
            self.uiFrame.notifySignals(type="alarm",value="alarm")
            self.uiFrame.notifySignals(type="pass",value="alarm")
        
        def exitStateBiz(self):
            self.infrasGroup["CETC_Alarm"].closeAlarm()
             
        def checkStateTrans(self):
            if self.ifToIdle():return ComplexEtcEntryBiz.EnterIdleState

    class FirstTradingState(AbstractCetcState):
        NO_IDEN_SERIAL = 0
        "首车正在交易状态"#核心交易状态！
        def __init__(self,infrasGroup,uiFrame,infoContainer = None):
            AbstractCetcState.__init__(self, infrasGroup, uiFrame, infoContainer)
            self.STATE_TIMEOUT = 60 #在这个状态不应停留超过60秒
            self.rsuTradeState = False   #ETC交易状态
            self.plateParsed = False    #号牌是否识别
            
        def entryStateBiz(self):
            SESSION["mainWnd"].log(msg = u"开始进行RSU交易...")
            self.photoCaptureThread.triggerCaptureAndParse(self.infrasGroup["PhotoCapture"],self.infrasGroup["PlatePhotoParser"])
                
        def doStateBiz(self):
            #周期RSU交易
            self.infoContainer["exited"] = 2
            self.infoContainer["state"] = "SUSPEND"
            res = self.infrasGroup["FrontendEtc"].notifyEntry()
            if res["rtnCode"] == FrontendEtc.SUCCESS:   #RSU交易成功
                self.rsuTradeState = True
                self.infoContainer["enterTime"] = res["enterTime"]
                self.infoContainer["plateNoByRfid"],self.infoContainer["vehicleTypeByRfid"] = [res["obuInfo"]["vehicleLicencePlateNumber"]],[res["obuInfo"]["vehicleClass"]] 
                self.infoContainer["obuInfo"] = res["obuInfo"]
                return True
            elif res["rtnCode"] == FrontendEtc.BLACK_LIST:  #黑名单车辆
                self.rsuTradeState = False
                self.infoContainer["plateNoByRfid"],self.infoContainer["vehicleTypeByRfid"] = [res["obuInfo"]["vehicleLicencePlateNumber"]],[res["obuInfo"]["vehicleClass"]] 
                self.infoContainer["enterTime"] = res["enterTime"]
                self.infoContainer["obuFailMsg"] = u"车辆黑名单"
                return True
            else:
                self.rsuTradeState = False
                self.infoContainer["enterTime"] = dateutil.nowTime() 
                self.infoContainer["plateNoByRfid"],self.infoContainer["vehicleTypeByRfid"] = [],[] 
                self.infoContainer["obuFailMsg"] = u"交易失败"
                time.sleep(0.01)
                return False

        def exitStateBiz(self):
            SESSION["mainWnd"].log(msg = u"RSU交易完成，结果:%s"%(u"成功" if self.rsuTradeState else u"失败"))
            self.infoContainer["photo"],self.infoContainer["plateNoByPhoto"], self.infoContainer["vehicleType"] =   \
                self.photoCaptureThread.getCaptureAndParseResult() 
            if self.rsuTradeState: #RSU交易成功了 ,使用OBU内的车牌号和车型
                self.infoContainer["plateNo"] = self.infoContainer["plateNoByRfid"][0]
                self.infoContainer["vehicleType"] = self.infoContainer["vehicleTypeByRfid"][0]
            else:   #RSU交易失败，使用号牌识别填写车牌和车型
                if self.infoContainer["plateNoByPhoto"] is not None:
                    self.infoContainer["plateNo"] = self.infoContainer["plateNoByPhoto"]
                else:
                    self.infoContainer["plateNo"] = u"未识别%d"%ComplexEtcEntryBiz.FirstTradingState.NO_IDEN_SERIAL
                    ComplexEtcEntryBiz.FirstTradingState.NO_IDEN_SERIAL+= 1
                    self.infoContainer["vehicleType"] = u"未知车型"
            rtn = TSStub.saveEntryRecord(self.infoContainer.toEntryRecord())
            self.infoContainer["entryRecordId"] = rtn["newPk"]

        def checkStateTrans(self):
            if self.rsuTradeState:  #RSU交易成功
                return ComplexEtcEntryBiz.FirstTradeSuccessState
            if self.infrasGroup["CETC_GroundCoils"].hasVehicle(3):  #压上3线圈，说明RSU交易失败
                return ComplexEtcEntryBiz.FirstRsuTradeFailState
            if self.ifToIdle():return ComplexEtcEntryBiz.EnterIdleState

        def bizOnTimeout(self):
            self.infrasGroup["LED"].showOnLed(u"ETC交易失败\n请继续前进或退出重试")
            self.infrasGroup["CETC_Alarm"].openAlarm()
            self.enterStateTime = time.time()   #更新超时时间，这样等再过这段时间就又触发超时一次


    class FirstRsuTradeFailState(AbstractCetcState):
        "RSU交易失败状态，这是一个暂态"
        def checkStateTrans(self):
            plateParsed = self.infoContainer["plateNoByPhoto"] is not None
            if plateParsed:return ComplexEtcEntryBiz.FailTradeWithParseState
            else:return ComplexEtcEntryBiz.FailTradeWithNoParseState

   
    class FirstTradeSuccessState(AbstractCetcState):
        "首车交易成功状态"
        def entryStateBiz(self):
            self.uiFrame.notifyActionInfras(type="rsu",value="success")
            info = self.infoContainer["obuInfo"]
            self.uiFrame.notifyVehicleInfo(
                                           tradeTime=dateutil.dtStr(self.infoContainer["enterTime"]),
                                           tradeType=u"RSU正常交易",
                                           cpuNetworkId = info["cardNetId"],
                                           cpuInnerId = info["cpuCardInnerId"],
                                           psamId = info["psamNo"],
                                           psamTradeSn = info["psamTransSerial"],
                                           obuid = info["obuid"],
                                           tacCode = info["tac"],
                                           plateNo = info["vehicleLicencePlateNumber"],
                                           vehicleType = info["vehicleClass"],
                                           vehicleState = u"正常"
                                           )
            self.infrasGroup["LED"].showOnLed(u"车牌 %s\n车型 %s\n金额 %2.f\n"%\
                                              (info["vehicleLicencePlateNumber"],
                                               info["vehicleClass"],
                                               info["cardRestMoney"]
                                               ))
            self.infrasGroup["Guardrail"].liftTheRail()
            self.uiFrame.notifyActionInfras(type="bar",value="acting")
        
        def checkStateTrans(self):
            if self.infrasGroup["CETC_GroundCoils"].isVehicleComes(3):  #3线圈上跳，表明正常交易的车辆进入了
                return ComplexEtcEntryBiz.FirstVehicleEnteredState
            if self.ifToIdle():return ComplexEtcEntryBiz.EnterIdleState

    class FailTradeWithParseState(AbstractCetcState):
        "交易失败但含有车牌识别结果"
        def entryStateBiz(self):
            self.uiFrame.notifyActionInfras(type="rsu",value="fail")
            self.uiFrame.notifyVehicleInfo(
                                           tradeTime=dateutil.dtStr(self.infoContainer["enterTime"]),
                                           tradeType=u"车牌识别",
                                           plateNo = self.infoContainer["plateNo"],
                                           vehicleType = self.infoContainer["vehicleType"],
                                           vehicleState = u"未知"
                                           )
            self.infrasGroup["LED"].showOnLed(u"%s\n车牌 %s\n3秒后放行，出场请走普通车道"%\
                                              (self.infoContainer["obuFailMsg"],self.infoContainer["plateNo"]))
            time.sleep(3)   #让他看一会儿LED再说
            self.infrasGroup["Guardrail"].liftTheRail()
            self.uiFrame.notifyActionInfras(type="bar",value="acting")
                
        def checkStateTrans(self):
            if (not self.infrasGroup["CETC_GroundCoils"].hasVehicle(2)) and self.infrasGroup["CETC_GroundCoils"].hasVehicle(3):
                #2线圈空闲且3线圈有车，说明车要进来了
                return ComplexEtcEntryBiz.FirstVehicleEnteredState
            if self.ifToIdle():return ComplexEtcEntryBiz.EnterIdleState

    class FailTradeWithNoParseState(AbstractCetcState):
        "交易失败且没有车牌识别结果"
        def entryStateBiz(self):
            self.uiFrame.notifyActionInfras(type="rsu",value="fail")
            self.uiFrame.notifyVehicleInfo(
                                           tradeTime=dateutil.dtStr(self.infoContainer["enterTime"]),
                                           tradeType=u"无识别",
                                           plateNo = u"未识别",
                                           vehicleType = u"未知",
                                           vehicleState = u"未知"
                                           )
            self.infrasGroup["LED"].showOnLed(u"%s\n车牌无识别\n3秒后放行，出场请走普通车道"%\
                                              self.infoContainer["obuFailMsg"])
          
            time.sleep(3)   #让他看一会儿LED再说
            #这种情况到底抬不抬杆？目前抬，后面要是不抬，在这个状态下搞它
            self.infrasGroup["Guardrail"].liftTheRail()
            self.uiFrame.notifyActionInfras(type="bar",value="acting")
        
        def checkStateTrans(self):
            if (not self.infrasGroup["CETC_GroundCoils"].hasVehicle(2)) and self.infrasGroup["CETC_GroundCoils"].hasVehicle(3):
                #2线圈空闲且3线圈有车，说明车要进来了
                return ComplexEtcEntryBiz.FirstVehicleEnteredState
            if self.ifToIdle():return ComplexEtcEntryBiz.EnterIdleState

    class FirstVehicleEnteredState(AbstractCetcState):
        "首车已进入状态"
        def entryStateBiz(self):
            TSStub.confirmEntryRecord({"entryRecordId":self.infoContainer["entryRecordId"],
                                               "plateNo":self.infoContainer["plateNo"],
                                               "entryId":self.infrasGroup.infrasGroupId,
                                               "centerTradingRecord":self.infoContainer.toCenterEnteringRecord()
                                               })
            self.uiFrame.notifyVehicleEntry(entryRecordId = self.infoContainer["entryRecordId"],
                                            entryExit = u"入场",
                                            enterTime = dateutil.dtStr(self.infoContainer["enterTime"]),
                                            entryExitId = self.infrasGroup.infrasGroupId,
                                            plateNo = self.infoContainer["plateNo"],
                                            vehicleType = self.infoContainer["vehicleType"],
                                            plateNoByPhoto = self.infoContainer["plateNoByPhoto"],
                                            plateNoByRfid = u",".join(self.infoContainer["plateNoByRfid"])
                                            )
                           
        def checkStateTrans(self):
            if self.infrasGroup["CETC_GroundCoils"].isVehicleComes(1):
                #一线圈上跳，可以开始下一个交易流程了
                return ComplexEtcEntryBiz.FirstTradingState
            if self.ifToIdle():return ComplexEtcEntryBiz.EnterIdleState

        def exitStateBiz(self):
            self.infrasGroup["LED"].showIdleMsgOnLed()
        
    def __init__(self,infrasGroup,uiFrame):
        AbstractComplexEtcChannel.__init__(self,infrasGroup,uiFrame)
        self.currentState = ComplexEtcEntryBiz.EnterIdleState(self.infrasGroup,self.uiFrame,self.infoContainer)
        self.start()
        
    
