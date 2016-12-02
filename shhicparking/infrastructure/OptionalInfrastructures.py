#encoding:utf-8
'''
Created on 2015-10-9
可选的基础设施

某些基础设施在出入口可能为空，在这种情况下，使用这里的可选设施
这里面的设施忽略具体设施应该承担的逻辑，但保持运行时正常
@author: user
'''
from AbstractInfrastructures import LED,Speaker,Camera,PhotoCapture,PlatePhotoParser,   \
    RfidReader,ManualControlledVehicleComes,GroundSensingCoil_lock,WhitelistProcessor,ParkingFeeCalculator

from shhicparking.server import TSStub
from shhicparking.util.dateutil import nowTime

class PesudoOptionalInfrastructures(LED,Speaker,Camera,PhotoCapture,PlatePhotoParser,WhitelistProcessor,
                                    RfidReader,ManualControlledVehicleComes,GroundSensingCoil_lock,
                                    ParkingFeeCalculator):
    def __init__(self):
        self.infrasId = "NO_EXISTS"
        self.lastLedMessage = None
        self.lastSpeakMessage = None
    
    def showOnLed(self,message):
        if self.lastLedMessage != message:
            self.lastLedMessage = message
            print '[PESUDO-LED]',message
    
    def speak(self,message):
        if self.lastSpeakMessage != message:
            self.lastSpeakMessage = message
            print '[PESUDO-SPEAKER]',message
    
    def startVedio(self,uiFrame):
        uiFrame.vedioFrame.setDisabled(True)
        uiFrame.vedioFrame.hide()

    def stopVedio(self):
        pass
    
    def capturePhoto(self):
        return None
    
    def parsePlateNo(self,photo=None):
        return None,None
#        return u"无图像",u"未知车型"
#        return u"京AF0236",u"小型车"
    
    def getAllTags(self):
        return [],[]
    
    def isManualControlAllowed(self):
        return False
        
    def manualAssertVehicleComes(self):
        pass
    
    def lockOppositeCoil(self):
        pass
    
    def notifyCoilLock(self):
        pass

    def checkFreeVehicle(self,plateNo,vehicleType,channelId):
        res = TSStub.checkFreeVehicle({"plateNo":plateNo,"vehicleType":vehicleType})
        if res["rtnCode"] == 0:
            return {"rtnCode":0,"info":u"非本场车辆"}
        else:
            now = nowTime()
            if (res["validTime"] != 0 and now < res["validTime"]) or \
                ( res["expireTime"] != 0 and now > res["expireTime"]):
                return {"rtnCode":2,"info":u"车辆已过期"}
            if res["selectedChannels"]!="" and channelId not in res["selectedChannels"].split(","):
                return {"rtnCode":3,"info":u"请绕行其他出入口"}
            return {"rtnCode":1,"info":u"正常白名单"}
            
            
    #以下是默认的计费插件，默认不计费
    def getCurrentTollDetailTable(self):
        '''获取当前计费明细表'''#格式：[[开始时间,结束时间,计费方式,费率,金额],]
        return []

    def getCurrentSum(self):
        '''获得当前计算金额数'''
        return 0

    def reloadScript(self):
        '''重新载入计费脚本'''
        pass
        
    def getScriptFile(self):
        '''获取计费脚本文件'''
        return None
        
    def calcActualParkingTimeAndFee(self,vehicleType,enterTime,exitTime,monthlyPayTimeInterval):
        '''计费并返回结果，返回值包含交易使用类型（错时停车、车位租赁，或""），及金额。'''
        #入参enterTime,exitTime为毫秒时间戳
        #monthlyPayTimeInterval，车辆包月（错时停车）数据，格式为[[开始日期,结束日期,开始时间(距当天毫秒),结束时间],]
        return "不计费",0
        
    def calcFee(self,vehicleType,parkingTime,exitTime):
        '''计算停车费，入参为车型及停车时间，出场时间'''
        return self.calcActualParkingTimeAndFee(vehicleType,exitTime-parkingTime,exitTime,[])[1]
    
    
    
    
    
    
    