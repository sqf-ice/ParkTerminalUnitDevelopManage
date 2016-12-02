#encoding:utf-8

'''停车场车道软件用户界面'''

from PyQt4.QtCore import SIGNAL,SLOT,QObject
from PyQt4.QtGui import QWidget
from PyQt4 import QtGui
from threading import Lock

class AUF:
    def __init__(self,widget,slotMethod):
        self.widget = widget
        self.slotMethod = slotMethod
    def __call__(self,**param):
        pq = `param`
        self.widget.emit(SIGNAL(self.slotMethod+"(QString)"),pq)

class UF:
    def __init__(self,widget,slotMethod):
        self.widget = widget
        self.slotMethod = slotMethod
        
    def __call__(self,qo):
        self.widget.__class__.__dict__[self.slotMethod](self.widget,eval(qo.__str__()))

def USE_AUF(widget):
    '''在生成界面Widget中使用此方法，可以将SLOT结尾的方法转换成槽方法，使用除SLOT外的部分作为函数名来异步调用
        SLOT方法中只能含有一个参数，同时传入该参数的对象应是dict格式，能够被repr和eval序列化
    '''
    for slotMethod in widget.__class__.__dict__:
        if slotMethod.endswith("SLOT"):
            print 'add signal:',slotMethod
            widget.connect(widget, SIGNAL(slotMethod+"(QString)"), UF(widget,slotMethod))
            widget.__dict__[slotMethod[:-4]] = AUF(widget,slotMethod)
                   
current_dlg_count = 0
dlg_show_lock = Lock() 

def showChannelBizDlg(dlg):
    global current_dlg_count
    dlg_show_lock.acquire()
    if current_dlg_count <= 0:
        dlg.setModal(False)
        current_dlg_count = 0
    else:
        dlg.setModal(False)
    QtGui.QDialog.show(dlg)
    current_dlg_count += 1
    dlg_show_lock.release()

def hideChannelBizDlg(dlg):
    global current_dlg_count
    dlg_show_lock.acquire()
    QtGui.QDialog.hide(dlg)
    current_dlg_count -= 1
    dlg_show_lock.release()


