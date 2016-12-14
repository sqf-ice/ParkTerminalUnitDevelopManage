#encoding:utf-8
'''
Created on 2016-9-19
复杂ETC车道出口界面
@author: zws
'''


from PyQt4 import QtCore, QtGui, uic
from PyQt4.Qt import pyqtSlot
from shhicparking.ui import USE_AUF
from AbstractComplexEtcChannelForm import AbstractComplexEtcChannelFrom
from ManualTollDlg import ManualTollDlg 


class ComplexEtcExitForm(AbstractComplexEtcChannelFrom):
    def __init__(self,parentForm,infrasGroupId,uiType="common"):
        AbstractComplexEtcChannelFrom.__init__(self, parentForm, infrasGroupId,uiType="common")
        self.infoGroup.setTitle(u"出场收费")
        self.manualTollDlg = ManualTollDlg(self)
        self.tradeTimeLabel.setText(u"出场时间")
        self.manualTollBtn.setEnabled(False)
        self.manualTollFinished = False
        
    def notifyVehicleOnCoilSLOT(self,param):
        AbstractComplexEtcChannelFrom.notifyVehicleOnCoilSLOT(self, param)
        
    def notifySignalsSLOT(self,param):
        AbstractComplexEtcChannelFrom.notifySignalsSLOT(self,param)
    
    def notifyActionInfrasSLOT(self,param):
        AbstractComplexEtcChannelFrom.notifyActionInfrasSLOT(self,param)
        
    def notifyVehicleInfoSLOT(self,param):
        AbstractComplexEtcChannelFrom.notifyVehicleInfoSLOT(self,param)
        
    def notifyVehicleExitSLOT(self,param):
        AbstractComplexEtcChannelFrom.notifyVehicleEntrySLOT(self,param)
        
    def notifyShouldManualTollSLOT(self,param):
        self.manualTollBtn.setEnabled(param["manual"])
     
    @pyqtSlot()
    def on_manualTollBtn_clicked(self):
        self.manualTollDlg.show(self.infoContainer)
