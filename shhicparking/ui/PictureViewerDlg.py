#encoding:utf-8
'''
Created on 2015-8-27
图片查看窗口
@author: user
'''
from PyQt4 import QtGui, QtCore, uic
from PyQt4.Qt import pyqtSlot
from PyQt4.QtGui import QMessageBox
from shhicparking.server import TSStub
from shhicparking.util import dateutil
import base64

class PictureViewerDlg(QtGui.QDialog):
    def __init__(self,parent):
        super( PictureViewerDlg, self ).__init__(parent=parent)
        uic.loadUi( "shhicparking/ui/uires/pictureViewerDlg.ui", self )
        
    def show(self,photo,title=None):
        QtGui.QDialog.show(self)
        self.label.setPixmap(photo)
        self.setWindowTitle(u"图片查看:"+title if title is not None else "")
        
    @pyqtSlot()
    def on_saveBtn_clicked(self):
        fn = QtGui.QFileDialog.getSaveFileName(self,u"保存图片","/", u"图片文件 (*.jpg);;所有文件(*.*)")
        if fn != '':
            if self.label.pixmap().save(fn):
                QMessageBox.information(self, u"保存图片",u"图片保存完成")
            else:
                QMessageBox.warning(self, u"保存图片",u"图片保存完成")
    
    @pyqtSlot()
    def on_closeBtn_clicked(self):
        self.label.clear()
        self.hide()
