# encoding:utf-8
'''
Created on 2016-11-17
车位管理主程序
@author: zws
'''
import ctypes
import sys, os

reload(sys)
sys.setdefaultencoding('utf-8')
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMessageBox
import logging, time

QtGui.QApplication.setStyle("cleanlooks")
app = QtGui.QApplication(sys.argv)

from shhicparking.ui.uires import parkClient
from shhicparking import SESSION
from shhicparking.infrastructure import initInfras, INFRAS_GROUPS
from kcht_complex_etc.ui.ComplexEtcEntryForm import ComplexEtcEntryForm
from kcht_complex_etc.biz.ComplexEtcEntryBiz import ComplexEtcEntryBiz


class TestMainWnd(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setWindowTitle(u"车位管理测试容器")
        self.slotFrameLayout = QtGui.QHBoxLayout()
        self.setLayout(self.slotFrameLayout)

    def log(self, msg):
        print "log:", msg

    def show(self):
        self.sf = ComplexEtcEntryForm(self, u'ETC入口')
        self.slotFrameLayout.addWidget(self.sf)
        ComplexEtcEntryBiz(INFRAS_GROUPS[u'ETC入口'], self.sf)
        QtGui.QDialog.show(self)
        self.sf.show()

    def closeEvent(self, evt):
        os._exit(0)


def initLocalLogger():
    '''初始化日志'''
    logger = logging.getLogger()
    hdlr = logging.FileHandler('logs/park-slot-log-%s.log' % time.strftime('%Y-%m-%d', time.localtime(time.time())))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(hdlr)
    logger.addHandler(console)
    logger.info(u"Kcht Park Slot Manager App launched")


if __name__ == '__main__':
        SESSION["mainWnd"] = TestMainWnd()
        initInfras()  # 初始化基础设施
        initLocalLogger()
        SESSION["mainWnd"].show()
        app.exec_()



