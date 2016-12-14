#encoding:utf-8
'''
Created on 2016-9-19
复杂高速ETC车道，出口逻辑
@author: zws
'''

from AbstractComplexEtcBiz import AbstractComplexEtcChannel,AbstractCetcState
from shhicparking import SESSION
from shhicparking.server import TSStub
from kcht_complex_etc.infras import FrontendEtc
from shhicparking.util import dateutil
import time
import base64

class ComplexEtcExitBiz(AbstractComplexEtcChannel):
    class ExitIdleState(AbstractCetcState):
        "空闲状态"
        def entryStateBiz(self):
            self.infoContainer.finish()
            self.uiFrame.notifyActionInfras()
            self.uiFrame.notifyVehicleInfo()
            self.uiFrame.notifyVehicleOnCoil()
            self.uiFrame.notifySignals()
            self.infrasGroup["LED"].showIdleMsgOnLed()
            self.infrasGroup["Guardrail"].dropTheRail()
        
        def checkStateTrans(self):
            gc = self.infrasGroup["CETC_GroundCoils"]
            if gc.hasVehicle(2) or gc.hasVehicle(3):
                return ComplexEtcExitBiz.UnexceptedEnterState
            if gc.hasVehicle(1):#一线圈触发
                return ComplexEtcExitBiz.FirstTradingState
    
    class UnexceptedEnterState(AbstractCetcState):
        "旁道误入告警状态"
        def entryStateBiz(self):
            SESSION["mainWnd"].log(msg = u"错误：车辆旁道误入")
            self.infrasGroup["LED"].showOnLed(u"旁道误入,请退出车道后重入!")
            self.infrasGroup["CETC_Alarm"].openAlarm()
            self.uiFrame.notifySignals(type="alarm",value="alarm")
            self.uiFrame.notifySignals(type="pass",value="alarm")
        
        def exitStateBiz(self):
            self.infrasGroup["CETC_Alarm"].closeAlarm()
             
        def checkStateTrans(self):
            if self.ifToIdle():return ComplexEtcExitBiz.ExitIdleState

    class FirstTradingState(AbstractCetcState):
        "首车正在交易状态"#核心交易状态！
        def __init__(self,infrasGroup,uiFrame,infoContainer = None):
            AbstractCetcState.__init__(self, infrasGroup, uiFrame, infoContainer)
            self.STATE_TIMEOUT = 60 #在这个状态不应停留超过60秒
            self.rsuTradeState = 0 #ETC交易状态:1-成功，2-需要转入人工，3-必须退出走人工车道
            self.plateParsed = False    #号牌是否识别
            
        def __loadEntryRecord(self,obuinfo,enterTime):
            "调取自己存的入场记录"
            record = TSStub.getNearestEntryRecord({"plateNo":obuinfo["vehicleLicencePlateNumber"]})
            if record is None or record["enterTime"] != enterTime :
                #如果没有入场记录，或者入场记录中的时间不符,那么就从OBU中逮出来一个；
                #并且生成伪入场记录
                pr = {
                    "enterTime":enterTime,
                    "entryId":u"未知",
                    "plateNo":self.infoContainer["plateNo"],
                    "vehicleType":self.infoContainer["vehicleType"],
                    "rfidParsePlateNoResult":u"无识别-协商",
                    "imgParsePlateNoResult":u"无识别-协商",
                    "enterImg":None,
                    "state":"PESUDO",
                    "ordering":0,
                    "exited":1
                    }
                res = TSStub.saveEntryRecord(pr)
                pr["id"] = res["newPk"]
                return pr
            else:
                record["enterImg"] = base64.b64decode(record["enterImg"])   #图片转换
                return record
        
        def entryStateBiz(self):
            SESSION["mainWnd"].log(msg = u"开始进行RSU交易...")
            self.photoCaptureThread.triggerCaptureAndParse(self.infrasGroup["PhotoCapture"],self.infrasGroup["PlatePhotoParser"])
                
        def doStateBiz(self):
            #周期RSU交易
            res = self.infrasGroup["FrontendEtc"].tollOnExit()
            if res["rtnCode"] == FrontendEtc.SUCCESS:   #RSU交易成功
                self.rsuTradeState = 1
                self.infoContainer["exitTime"] = res["exitTime"]
                self.infoContainer["state"] = u"TRUSTED"   
                self.infoContainer["tradeType"] = u"FRONT_ETC"   #交易类型：前台ETC
                self.infoContainer["parkingFee"] = res["fee"]   #停车费即实际扣费
                self.infoContainer["cash"] = 0  #现金收费为0
                self.infoContainer["plateNoByRfid"],self.infoContainer["vehicleTypeByRfid"] = [res["obuInfo"]["vehicleLicencePlateNumber"]],[res["obuInfo"]["vehicleClass"]] 
                self.infoContainer["obuInfo"] = res["obuInfo"]
                self.infoContainer["entryRecord"] = self.__loadEntryRecord(res["obuInfo"],res["enterTime"])
                return True
            elif res["rtnCode"] == FrontendEtc.BLACK_LIST:  #黑名单车辆
                self.rsuTradeState = 2
                self.infoContainer["plateNoByRfid"],self.infoContainer["vehicleTypeByRfid"] = [res["obuInfo"]["vehicleLicencePlateNumber"]],[res["obuInfo"]["vehicleClass"]] 
                self.infoContainer["state"] = u"TRUSTED"   
                self.infoContainer["exitTime"] = res["exitTime"]
                self.infoContainer["obuInfo"] = res["obuInfo"]
                self.infoContainer["parkingFee"] = res["fee"]   #停车费即实际扣费
                self.infoContainer["entryRecord"] = self.__loadEntryRecord(res["obuInfo"],res["enterTime"])
                self.infoContainer["obuFailMsg"] = u"黑名单，请等待人工收费或重入普通车道"
                return True
            elif res["rtnCode"] == FrontendEtc.BALANCE_NOT_ENOUGH:  #余额不足
                self.rsuTradeState = 2
                self.infoContainer["plateNoByRfid"],self.infoContainer["vehicleTypeByRfid"] = [res["obuInfo"]["vehicleLicencePlateNumber"]],[res["obuInfo"]["vehicleClass"]] 
                self.infoContainer["state"] = u"TRUSTED"   
                self.infoContainer["exitTime"] = res["exitTime"]
                self.infoContainer["parkingFee"] = res["fee"]   #停车费即实际扣费
                self.infoContainer["obuInfo"] = res["obuInfo"]
                self.infoContainer["entryRecord"] = self.__loadEntryRecord(res["obuInfo"],res["enterTime"])
                self.infoContainer["obuFailMsg"] = u"余额不足 请等待人工或退出"
                return True 
            else:
                self.rsuTradeState = 3 
                self.infoContainer["obuFailMsg"] = u"OBU出口交易失败，请重入普通车道"
                time.sleep(0.01)
                return False

        def exitStateBiz(self):
            SESSION["mainWnd"].log(msg = u"RSU交易完成，结果:%s"%(u"成功" if self.rsuTradeState == 1 else u"失败"))
            self.infoContainer["photo"],self.infoContainer["plateNoByPhoto"], self.infoContainer["vehicleType"] =   \
                self.photoCaptureThread.getCaptureAndParseResult() 
            if self.rsuTradeState != 3: #RSU读取成功了 ,使用OBU内的车牌号和车型
                self.infoContainer["plateNo"] = self.infoContainer["plateNoByRfid"][0]
                self.infoContainer["vehicleType"] = self.infoContainer["vehicleTypeByRfid"][0]

        def checkStateTrans(self):
            if self.rsuTradeState == 1:  #RSU交易成功
                return ComplexEtcExitBiz.FirstTradeSuccessState
            if self.infrasGroup["CETC_GroundCoils"].hasVehicle(3):  #压上3线圈，说明RSU交易失败
                if self.rsuTradeState == 2:
                    return ComplexEtcExitBiz.WaitForManualState
                elif self.rsuTradeState == 3:
                    return ComplexEtcExitBiz.ExitAlarmState
            if self.ifToIdle():return ComplexEtcExitBiz.ExitIdleState

        def bizOnTimeout(self):
            self.infrasGroup["LED"].showOnLed(u"ETC交易失败\n请继续前进或退出重试")
            self.infrasGroup["CETC_Alarm"].openAlarm()
            self.enterStateTime = time.time()   #更新超时时间，这样等再过这段时间就又触发超时一次
            
    class FirstTradeSuccessState(AbstractCetcState):
        "首车交易成功状态"
        def entryStateBiz(self):
            self.uiFrame.notifyActionInfras(type="rsu",value="success")
            info = self.infoContainer["obuInfo"]
            self.uiFrame.notifyVehicleInfo(
                                           tradeTime=dateutil.dtStr(self.infoContainer["exitTime"]),
                                           tradeType=u"RSU正常交易",
                                           cpuNetworkId = info["cardNetId"],
                                           cpuInnerId = info["cpuCardInnerId"],
                                           psamId = info["psamNo"],
                                           psamTradeSn = info["psamTransSerial"],
                                           obuid = info["obuid"],
                                           tacCode = info["tac"],
                                           plateNo = info["vehicleLicencePlateNumber"],
                                           vehicleType = info["vehicleClass"],
                                           vehicleState = u"正常",
                                           tollFee = u"%.2f 元"%self.infoContainer["parkingFee"]
                                           )
            self.infrasGroup["LED"].showOnLed(u"车牌 %s\n车型 %s\n金额 %.2f\n交易成功"%\
                                              (info["vehicleLicencePlateNumber"],
                                               info["vehicleClass"],
                                               self.infoContainer["parkingFee"]
                                               ))
            self.infrasGroup["Guardrail"].liftTheRail()
            self.uiFrame.notifyActionInfras(type="bar",value="acting")
        
        def checkStateTrans(self):
            "首车交易成功，直接进入出场状态"
            if self.infrasGroup["CETC_GroundCoils"].isVehicleComes(2) or self.infrasGroup["CETC_GroundCoils"].isVehicleComes(3):
                return ComplexEtcExitBiz.FirstVehicleExitedState
            if self.ifToIdle():return ComplexEtcExitBiz.ExitIdleState
            

    class FirstVehicleExitedState(AbstractCetcState):
        "首车已出场状态"
        def entryStateBiz(self):
            res = TSStub.saveExitTradingRecord(self.infoContainer.toExitRecord())
            self.infoContainer["exitRecordId"] = res["exitRecordId"]
            self.uiFrame.notifyVehicleExit(entryRecordId = self.infoContainer["exitRecordId"],
                                            entryExit = u"出场",
                                            enterTime = dateutil.dtStr(self.infoContainer["exitTime"]),
                                            entryExitId = self.infrasGroup.infrasGroupId,
                                            plateNo = self.infoContainer["plateNo"],
                                            vehicleType = self.infoContainer["vehicleType"],
                                            plateNoByPhoto = self.infoContainer["plateNoByPhoto"],
                                            plateNoByRfid = u",".join(self.infoContainer["plateNoByRfid"])
                                            )
        def checkStateTrans(self):
            if self.infrasGroup["CETC_GroundCoils"].isVehicleComes(1):
                #一线圈上跳，可以开始下一个交易流程了
                return ComplexEtcExitBiz.FirstTradingState
            if self.ifToIdle():return ComplexEtcExitBiz.ExitIdleState

        def exitStateBiz(self):
            self.infrasGroup["LED"].showIdleMsgOnLed()
             
    class ExitAlarmState(AbstractCetcState):
        "退出报警状态"
        def entryStateBiz(self):
            SESSION["mainWnd"].log(msg=u"错误：出口OBU交易失败，需要车辆退出")
            self.infrasGroup["LED"].showOnLed(u"交易失败\n无OBU\n请走普通人工车道")
            self.infrasGroup["CETC_Alarm"].openAlarm()
            self.uiFrame.notifySignals(type="alarm",value="alarm")
            self.uiFrame.notifySignals(type="pass",value="alarm")
       
        def exitStateBiz(self):
            self.infrasGroup["CETC_Alarm"].closeAlarm()
            
        def checkStateTrans(self):
            if self.ifToIdle():return ComplexEtcExitBiz.ExitIdleState

    class WaitForManualState(AbstractCetcState):
        "等待人工干预状态"
        def __init__(self,infrasGroup,uiFrame,infoContainer = None):
            AbstractCetcState.__init__(self, infrasGroup, uiFrame, infoContainer)
            self.STATE_TIMEOUT = 300 #在这个状态不应停留超过300秒
            
        def entryStateBiz(self):
            self.uiFrame.notifyActionInfras(type="rsu",value="fail")
            self.uiFrame.notifyShouldManualToll(manual = True)
            info = self.infoContainer["obuInfo"]
            self.uiFrame.notifyVehicleInfo(
                                           tradeTime=dateutil.dtStr(self.infoContainer["exitTime"]),
                                           tradeType=u"等待人工交易",
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
 
            self.infrasGroup["LED"].showOnLed(u"车牌 %s\n金额 %.2f\n%s"%\
                                              (self.infoContainer["plateNo"],
                                               self.infoContainer["parkingFee"],
                                               self.infoContainer["obuFailMsg"]
                                               ))
            self.infrasGroup["CETC_Alarm"].openAlarm() 
        
        def exitStateBiz(self):
            self.infrasGroup["CETC_Alarm"].closeAlarm()
            self.uiFrame.notifyShouldManualToll(manual = False)
            self.uiFrame.manualTollFinished = False
            
        def checkStateTrans(self):
            if self.uiFrame.manualTollFinished:
                return ComplexEtcExitBiz.ManualTollSuccessState
            if self.ifToIdle():return ComplexEtcExitBiz.ExitIdleState
    
    
    class ManualTollSuccessState(AbstractCetcState):
        "人工缴费完成"
        def entryStateBiz(self):
            self.infrasGroup["Guardrail"].liftTheRail()
            self.uiFrame.notifyActionInfras(type="bar",value="acting")
            self.uiFrame.notifyActionInfras(type="ic",value="success")
            info = self.infoContainer["obuInfo"]
            self.uiFrame.notifyVehicleInfo(
                                           tradeTime=dateutil.dtStr(self.infoContainer["exitTime"]),
                                           tradeType=u"刷卡-人工消费",
                                           cpuNetworkId = info["cardNetId"],
                                           cpuInnerId = info["cpuCardInnerId"],
                                           psamId = info["psamNo"],
                                           psamTradeSn = info["psamTransSerial"],
                                           obuid = info["obuid"],
                                           tacCode = info["tac"],
                                           plateNo = info["vehicleLicencePlateNumber"],
                                           vehicleType = info["vehicleClass"],
                                           vehicleState = u"正常",
                                           tollFee = u"%.2f 元"%self.infoContainer["parkingFee"]
                                           )
        def checkStateTrans(self):
            "首车交易成功，直接进入出场状态"
            return ComplexEtcExitBiz.FirstVehicleExitedState
        
    
    def __init__(self,infrasGroup,uiFrame):
        AbstractComplexEtcChannel.__init__(self,infrasGroup,uiFrame)
        self.currentState = ComplexEtcExitBiz.ExitIdleState(self.infrasGroup,self.uiFrame,self.infoContainer)
        self.start()
