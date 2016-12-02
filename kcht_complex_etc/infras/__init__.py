#encoding:utf-8

#复杂ETC车道基础设施
'''
地感线圈：4级：触发开始、触发结束、抓拍
    
LED显示 、语音、报警器
语音播报
雨棚灯
刷卡机
RSU

'''
class FrontendEtc:  #V2.00.00新增，目前没有放在默认实现中，由ETC停车场车道逻辑单独引用-20160920
    "前端电子收费设施"
    #定义扣费失败的异常
    class NotagException(Exception):pass    #无电子标签（扣费载体）异常
    class BalanceNotEnoughException(Exception):pass #余额不足异常
    class BlacklistException(Exception):pass    #车辆属于黑名单异常
    class NoEntryRecordException(Exception):pass    #无入场记录异常
    
    def getStationInfo(self):
        "获得站级的信息"
        #返回值应包含：{"roadNetworkId":"路网编号","roadCompanyId":"路公司编号","ownerId":"业主编号","stationId":"站编号","areaId":"广场号","channelId":"车道编号"} 
        
    def notifyEntry(self,entryId,enterTime,plateNo=None,vehicleType=None):
        "车辆进场时的收费初始化"#入参为车道、进入时间（毫秒戳），车牌号和车型可选，因为前端电子收费往往与电子识别一体
        #设置不成功时抛出上面的相应异常
        raise Exception("No implement for FrontendEtc")
    
    def tollOnExit(self,info,exitId,exitTime,fee,plateNo=None,vehicleType=None):
        "车辆出场时收费"#入参为车道、出场时间（毫秒戳），收费金额。车牌号和车型可选，因为前端电子收费往往与电子识别一体
        #设置不成功时抛出上面的相应异常
        raise Exception("No implement for FrontendEtc")
    
    def getMessage(self):
        "返回当前消息"
        raise Exception("No implement for FrontendEtc")
    
    
class CETC_GroundCoils:
    "复杂ETC车道线圈控制器"
    def hasVehicle(self,coilNum):
        "地感上是否有车，入参是地感编号1-3"    #有车返回True，没车返回False
        raise Exception("No implement for CETC_GroundCoils")

    def isVehicleComes(self,coilNum,timeWnd = 2):
        "是否有车压上地感（上跳沿）"#入参是地感编号，和时间窗口（秒）。即检查timeWnd时间内，地感coilNum是否存在一个上跳沿，如果有，返回True，否则返回False
        raise Exception("No implement for CETC_GroundCoils")
    
    def isVehicleLeaves(self,coilNum,timeWnd = 2):
        "是否有车离开地感（下跳沿）"#入参是地感编号，和时间窗口（秒）。即检查timeWnd时间内，地感coilNum是否存在一个下跳沿，如果有，返回True，否则返回False
        raise Exception("No implement for CETC_GroundCoils")
        
#道闸控制器，仍然使用标准模型的Guardrail
#摄像机仍然使用标准模型的PhotoCapture、PlatePhotoParser、Camera
#RFID识别使用标准模型的RfidReader
#前台电子扣费设施使用标准模型的FrontendEtc

class CETC_Alarm:
    "ETC车道报警器设施"
    def openAlarm(self,alarmNo = 0):
        "打开报警器"#入参可选，是报警器号
        raise Exception("No implement for CETC_Alarm")
    
    def closeAlarm(self,alarmNo = 0):
        "关闭报警器"#入参可选，是报警器号
        raise Exception("No implement for CETC_Alarm")


class CETC_CanopyLights:
    "ETC车道雨棚灯设施"
    def notifyNormal(self):
        "通知雨棚灯显示正常"
        raise Exception("No implement for CETC_CanopyLights")
    
    def notifyWrong(self):
        "通知雨棚灯显示异常"
        raise Exception("No implement for CETC_CanopyLights")






