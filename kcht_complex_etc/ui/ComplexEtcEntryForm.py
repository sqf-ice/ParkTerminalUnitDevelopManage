#encoding:utf-8
'''
Created on 2016-9-19
复杂ETC车道入口界面
@author: zws
'''
from PyQt4 import QtCore, QtGui, uic
from PyQt4.Qt import pyqtSlot
from shhicparking.ui import USE_AUF
from AbstractComplexEtcChannelForm import AbstractComplexEtcChannelFrom,BP_ETC,BP_RED_CROSS,BP_GREEN_ARROW


class ComplexEtcEntryForm(AbstractComplexEtcChannelFrom):
    def __init__(self,parentForm,infrasGroupId,uiType="common"):
        AbstractComplexEtcChannelFrom.__init__(self, parentForm, infrasGroupId,uiType="common")
        self.tollFee.hide()
        self.tollFeeLabel.hide()
        self.manualTollBtn.hide()
        self.infoGroup.setTitle(u"车辆入场")
        self.tradeTimeLabel.setText(u"入场时间")
        self.icLabel.hide() #入口不需要刷卡机
        self.icTitleLabel.hide()

    def notifyVehicleOnCoilSLOT(self,param):
        AbstractComplexEtcChannelFrom.notifyVehicleOnCoilSLOT(self, param)
        
    def notifySignalsSLOT(self,param):
        AbstractComplexEtcChannelFrom.notifySignalsSLOT(self,param)
    
    def notifyActionInfrasSLOT(self,param):
        AbstractComplexEtcChannelFrom.notifyActionInfrasSLOT(self,param)
        
    def notifyVehicleInfoSLOT(self,param):
        AbstractComplexEtcChannelFrom.notifyVehicleInfoSLOT(self,param)
        
    def notifyVehicleEntrySLOT(self,param):
        AbstractComplexEtcChannelFrom.notifyVehicleEntrySLOT(self,param)
        
        
        
        
        