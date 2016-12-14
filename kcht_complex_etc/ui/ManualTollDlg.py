#encoding:utf-8
'''
Created on 2016-12-7
手动收费对话框
@author: zws
'''
from PyQt4 import QtCore, QtGui, uic
from PyQt4.Qt import pyqtSlot
from shhicparking.util import dateutil

from shhicparking.server import TSStub


class ManualTollDlg(QtGui.QDialog):
    def __init__(self,parent):
        QtGui.QDialog.__init__(self,parent)
        uic.loadUi("kcht_complex_etc/ui/manualTollDlg.ui", self)
        
    def show(self,infoContainer):
        QtGui.QDialog.show(self)
        self.infoContainer = infoContainer
        self.confirmManualTollBtn.setDisabled(True) #初始不能直接收现金
        self.__showVehicleInfo()
        self.__startIccTrade()

        
    def __showVehicleInfo(self):
        self.plateNo.setText(self.infoContainer["plateNo"])
        self.vehicleType.setText(self.infoContainer["vehicleType"])
        self.obuid.setText(self.infoContainer["obuInfo"]["obuid"])
        self.cpuInnerId.setText(self.infoContainer["obuInfo"]["cpuCardInnerId"])
        self.enterTime.setText(dateutil.dtStr(self.infoContainer["entryRecord"]["enterTime"]))
        self.exitTime.setText(dateutil.dtStr(self.infoContainer["exitTime"]))
        self.tollFee.setText(u"%.2f 元"%self.infoContainer["parkingFee"])
        ep = QtGui.QPixmap()
        ep.loadFromData(self.infoContainer["entryRecord"]["enterImg"])
        self.enterPhoto.setPixmap(ep)
        xp = QtGui.QPixmap()
        xp.loadFromData(self.infoContainer["photo"])
        self.exitPhoto.setPixmap(xp)

    def __startIccTrade(self):
        self.confirmManualTollBtn.setEnabled(True)
        pass    #开始等待IC卡刷卡交易，如果IC卡直接交易成功，则直接结束人工收费，否则显示确认人工收费按钮
    
    @pyqtSlot()   
    def on_confirmManualTollBtn_clicked(self):
        self.parent().manualTollFinished = True
        self.infoContainer["tradeType"] = "CASH"    #现金收费
        self.infoContainer["cash"] = self.infoContainer["parkingFee"]
        self.hide()
    
    @pyqtSlot()
    def on_cancelBtn_clicked(self):
        self.hide()

        