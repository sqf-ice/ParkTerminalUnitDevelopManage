#encoding:utf-8
'''
Created on 2016-9-27
复杂ETC出入口车道界面
@author: user
'''
from PyQt4 import QtCore, QtGui, uic
from PyQt4.Qt import pyqtSlot
from shhicparking.ui import USE_AUF
from shhicparking.infrastructure import INFRAS_GROUPS


BP_SMALL_CAR = QtGui.QPixmap(":sketch/smallCar.png")
BP_RED_ALARM = QtGui.QPixmap(":etc/redalarmlight.gif")
BP_GREEN_ALARM = QtGui.QPixmap(":etc/greenalarmlight.png")
BP_GREEN_ARROW = QtGui.QPixmap(":etc/greenarrow.png")
BP_RED_CROSS = QtGui.QPixmap(":etc/nopass.png")
BP_ETC = QtGui.QPixmap(":etc/etc-green.png")
BP_BAR_CLOSE = QtGui.QPixmap(":sketch/barClose.png")
BP_BAR_OPEN = QtGui.QPixmap(":sketch/barOpen.png")
BP_ERROR = QtGui.QPixmap(":etc/nopass.png")
BP_RSU = QtGui.QPixmap(":etc/rsu.png")
BP_RSU_SUCEESS = QtGui.QPixmap(":etc/rsu-success.png")
BP_RSU_FAIL = QtGui.QPixmap(":etc/rsu-fail.png")

class AbstractComplexEtcChannelFrom(QtGui.QWidget):
    def __init__(self,parentForm,infrasGroupId,uiType):
        QtGui.QFrame.__init__(self,parentForm)
        self.infrasGroup = INFRAS_GROUPS[infrasGroupId]
        if uiType == "common":
            uic.loadUi("kcht_complex_etc/ui/complexEtcChannelForm.ui",self)
        elif uiType == "simple":
            uic.loadUi("kcht_complex_etc/ui/complexEtcChannelSimpleForm.ui",self)
        self.infoContainer = None   #普通信息容器
        USE_AUF(self)

        #初始化场站、车道信息到界面
        si = self.infrasGroup["FrontendEtc"].getStationInfo()
        for k in ["roadNetworkId","roadCompanyId","ownerId","stationId","areaId","channelId"] :
            self.__dict__[k].setText(si[k])

        
    def notifyVehicleOnCoilSLOT(self,param):
        #通知界面地感上有车,param中含有coilNum(地感号)，isVehicleOn（是否有车），如果coilNum为0，则表示全部;如果参数空，则全部置位空闲
        cs = [self.coil1Label,self.coil2Label,self.coil3Label]
        if len(param) == 0:
            for c in cs:c.clear()
            return
        vc = None
        if param["coilNum"] == 0:
            vc = cs
        else:vc = [cs[param["coilNum"]-1]]
        if param["isVehicleOn"]:
            for c in vc:c.setPixmap(BP_SMALL_CAR)
        else:
            for c in vc:c.clear()
        
    def notifySignalsSLOT(self,param):
        #通知界面信号变化，param中含有：type（类型），value（状态（idle,alarm,error））
        #其中，type包括：alarm(报警灯),pass（通行指示），etc（雨棚灯）
        #如果param为空，则表示全清空
        if len(param) == 0:
            self.alarmLabel.setPixmap(BP_GREEN_ALARM)
            self.passLabel.setPixmap(BP_GREEN_ARROW)
            self.etcLabel.setPixmap(BP_ETC)
            return
        
        if param["type"] == "alarm":
            if param["value"] == "idle":
                self.alarmLabel.setPixmap(BP_GREEN_ALARM)
            elif param["value"] == "alarm":
                self.alarmLabel.setPixmap(BP_RED_ALARM)
            elif param["value"] == "error":
                self.alarmLabel.setPixmap(BP_ERROR)
        elif param["type"] == "pass":
            if param["value"] == "idle":
                self.passLabel.setPixmap(BP_GREEN_ARROW)
            elif param["value"] == "alarm":
                self.passLabel.setPixmap(BP_RED_CROSS)
            elif param["value"] == "error":
                self.passLabel.setPixmap(BP_ERROR)
        elif param["type"] == "etc":
            if param["value"] == "idle":
                self.etcLabel.setPixmap(BP_ETC)
            elif param["value"] == "alarm":
                self.etcLabel.setPixmap(BP_RED_CROSS)
            elif param["value"] == "error":
                self.etcLabel.setPixmap(BP_ERROR)
    
    def notifyActionInfrasSLOT(self,param):
        #通知界面动作变化，param中包含有:type（类型），value（状态（idle,acting,success,fail））
        #type包含：bar（道闸），rsu（RSU）,ic（IC读卡器）
        if len(param) == 0:
            self.barLabel.setPixmap(BP_BAR_CLOSE)
            return
        if param["type"] == "bar": 
            if param["value"] == "idle":
                self.barLabel.setPixmap(BP_BAR_CLOSE)
            elif param["value"] == "acting":
                self.barLabel.setPixmap(BP_BAR_OPEN)
        elif param["type"] == "rsu":    #目前不管RSU图标的动作
            if param["value"] == "idle":
                self.rsuLabel.setPixmap(BP_RSU)
            elif param["value"] == "acting":
                pass
            elif param["value"] == "fail":
                self.rsuLabel.setPixmap(BP_RSU_FAIL )
            elif param["value"] == "success":
                self.rsuLabel.setPixmap(BP_RSU_SUCEESS )
        

    def notifyVehicleInfoSLOT(self,param):
        #通知界面车辆信息param中包含的东西就是控件的名字
        #若param中为空，则清空界面
        ctrlMap = {
                   "tradeTime":self.tradeTime,
                   "tradeType":self.tradeType,
                   "cpuNetworkId":self.cpuNetworkId,
                   "cpuInnerId":self.cpuInnerId,
                   "psamId":self.psamId,
                   "psamTradeSn":self.psamTradeSn,
                   "obuid":self.obuid,
                   "tacCode":self.tacCode,
                   "plateNo":self.plateNo,
                   "vehicleType":self.vehicleType,
                   "vehicleState":self.vehicleState,
                   "tollFee":self.tollFee,
                   }
        if len(param) == 0:
            for k in param:ctrlMap[k].clear()
        else:
            for k in param:ctrlMap[k].setText(param[k])
                
       
        
        