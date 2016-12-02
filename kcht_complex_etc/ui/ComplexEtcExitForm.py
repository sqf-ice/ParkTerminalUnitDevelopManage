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


class ComplexEtcExitForm(AbstractComplexEtcChannelFrom):
    def __init__(self,parentForm,infrasGroupId,uiType="common"):
        AbstractComplexEtcChannelFrom.__init__(self, parentForm, infrasGroupId,uiType="common")
        self.infoGroup.setTitle(u"出场收费")
        self.tradeTimeLabel.setText(u"出场时间")
        
       
