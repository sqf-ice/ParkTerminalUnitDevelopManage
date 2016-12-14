#encoding:utf-8
'''
Created on 2016-12-8
发卡器出口交易实现，基于科畅慧通发卡器
@author: kcht
'''

from shhicparking.infrastructure.AbstractInfrastructures import *
from kcht_complex_etc.infras import CETC_ICCTrader
from issuerdevice import RSU
import time

class KchtCpuCardIssuerTrader(AbstractInfrastructure,CETC_ICCTrader):
    def __init__(self,infrasId,props):
        AbstractInfrastructure.__init__(self, infrasId, props)
        self.stationInfo = {"roadNetworkId":props[u"路网编号"],"roadCompanyId":props[u"路公司编号"]
                            ,"ownerId":props[u"业主编号"],"stationId":props[u"站编号"]
                            ,"areaId":props[u"广场号"],"channelId":props[u"车道编号"]}
        self.psamSlot = int(props[u"PSAM卡槽号"])
        self.currentIcc  = {}   #当前IC卡信息
        self.currentIccLastStation = {} #上次过站信息
        self.reader = RSU()
        self.reader.setTimeout(1000)
        self.reader.RSU_Open(2, 0, 0)
        
    def getStationInfo(self):
        "获得站级的信息"
        #返回值应包含：{"roadNetworkId":"路网编号","roadCompanyId":"路公司编号","ownerId":"业主编号","stationId":"站编号","areaId":"广场号","channelId":"车道编号"} 
        return self.stationInfo 

    def readICCInfo(self):
        "读取ICC信息"#包含0015文件（卡片发行信息）、0019文件（过站信息），及0002文件（余额）
        ret,dataLength,Data,ReturnStatus = self.reader.HFActive(200)
        if ret != 0:return None,None #未寻到卡
        ret = self.__initPsam()   #IC刷卡器不常用，因此每次寻到卡后都复位一次PSAM，应该更好一些吧
        if ret != 0:
            print 'PSAM reset fail!'
            return None,None #PSAM卡激活异常，也认为寻不到卡
        if self.__readICCInfos() == 0:
            return self.currentIcc,self.currentIccLastStation
        
    def __initPurcheAndWriteUnionFile(self,fee):
        tradeTimeInSeconds = int(time.time())
        tradeUnixTime = "%.8x"%tradeTimeInSeconds 
        tradeTime = time.strftime("%Y%m%d%H%M%S",time.localtime(tradeTimeInSeconds))
        
        file0019 = self.stationInfo[u"roadNetworkId"]+self.stationInfo[u"stationId"]+self.stationInfo[u"channelId"]+ \
                tradeUnixTime+self.currentIccLastStation["vehicleType"]+ \
                "02" + "00"*9 +  \
                "00000000"  +     \
                self.currentIcc["vehicleLicencePlateNumber"] +\
                "00"*4  
                #出入口状态：02-MTC出口，标志站：9字节全0
                #收费员工号，班次号，暂时写0，后面改
                #4字节预留
        write_union_cmd = "3080dcaac82baa2900" + file0019
        debit_money = "%.8x"%fee if self.currentIcc["cardType"] == "17" or self.currentIcc["cardRestMoney"] > fee  else "00"*4  
        #记账卡，或储值卡足够扣款，那么就扣款，并写过站信息
        init_purchase_cmd = "10805003020b" +"01" + debit_money + self.psamTerminalId  #其他情况，现金收费，卡中扣款0元
        ret,APDULIST,Data,ReturnStatus = self.reader.HFCmd(2, init_purchase_cmd+write_union_cmd)
        if ret!=0 or ReturnStatus !=0:return CETC_ICCTrader.ICC_INIT_PURCHE_ERROR,None
        initPurcheRes = {}
        initPurcheRes["icc_random_for_mac1"] = Data[2:][22:30]
        initPurcheRes["icc_trade_sn"] = Data[2:][8:12]
        initPurcheRes["icc_trade_key_version"] = Data[2:][18:20]
        initPurcheRes["icc_trade_key_id"] = Data[2:][20:22]
        initPurcheRes["debit_money"] = debit_money
        initPurcheRes["tradeUnixTime"] = tradeUnixTime 
        initPurcheRes["tradeTime"] = tradeTime 
        return 0,initPurcheRes
    
    def __chiperMac1(self,initPurcheRes):
        cmd = "8070000024"+initPurcheRes["icc_random_for_mac1"] + initPurcheRes["icc_trade_sn"] + initPurcheRes["debit_money"]+\
            "09" + initPurcheRes["tradeTime"] + \
            initPurcheRes["icc_trade_key_version"] + initPurcheRes["icc_trade_key_id"]+\
            self.currentIcc["icc_card_sn"] +self.currentIcc["icc_card_provider"]
            #交易类型：09-复合消费
        APDU = "%.2x%s"%(len(cmd)/2,cmd)
        ret,APDUList,Data = self.reader.PSAM_CHANNEL(self.psamSlot, 1, APDU)       
        if ret != 0:return CETC_ICCTrader.PSAM_CHIPER_ERROR,None
        chiperMacRes ={}
        chiperMacRes["terminal_trade_sn_and_mac1_ack"] = Data[2:][0:16]
        chiperMacRes["terminal_trade_sn"] = Data[2:][0:8]
        chiperMacRes["mac1"] = Data[2:][8:16]
        chiperMacRes["tradeTime"] = initPurcheRes["tradeTime"]
        return 0,chiperMacRes

    def __debitPurche(self,chiperMacRes):
        debit_purche = "14805401000f" + chiperMacRes["terminal_trade_sn"] + \
            chiperMacRes["tradeTime"] + chiperMacRes["mac1"]
        print 'debit_purche apdu:',debit_purche 
        ret,APDUList,Data,ReturnStatus = self.reader.HFCmd(1, debit_purche)
        if ret != 0  or ReturnStatus !=0:return CETC_ICCTrader.DEBIT_PURCH_ERROR 
        if Data[2:][16:20] != "9000":return CETC_ICCTrader.DEBIT_PURCH_ERROR 
        return 0
        

    def tollOnExit(self,fee):
        ret,initPurcheRes = self.__initPurcheAndWriteUnionFile(fee)
        if ret !=0 :return ret
        ret,chiperMacRes = self.__chiperMac1(initPurcheRes)
        if ret !=0 :return ret
        ret = self.__debitPurche(chiperMacRes)
        if ret != 0:return ret
        
        if initPurcheRes["debit_money"] != "00000000":
            pass    #TODO实际扣费不是0，说明ETC交易成功了，上传到清分中心
        
        return 0
        
    def __initPsam(self):
        ret,rlen,Data = self.reader.PSAM_Reset(self.psamSlot, 0)    #复位PSAM
        #读0016文件
        ret,APDUList,Data = self.reader.PSAM_CHANNEL(self.psamSlot, 1, "0500B0960006")
        if ret!=0:return CETC_ICCTrader.PSAM_CMD_ERROR
        apduLength = int(Data[:2],16)
        if Data[2:][apduLength*2-4:apduLength*2] != "9000":return CETC_ICCTrader.PSAM_CMD_ERROR 
        self.psamTerminalId = Data[2:14]    #PSAM卡ID
        #选择DF01文件
        ret,APDUList,Data = self.reader.PSAM_CHANNEL(self.psamSlot, 1, "0700A4000002DF01")
        if ret!=0:return CETC_ICCTrader.PSAM_CMD_ERROR
        return 0

    def __processFileReadResult(self,ret,APDUList,Data,ReturnStatus):
        if ret !=0 or ReturnStatus !=0:return CETC_ICCTrader.READ_ICC_FILE_FAIL,None
        apduLength = int(Data[:2],16)
        if Data[2:][apduLength*2-4:apduLength*2] != "9000":return CETC_ICCTrader.ICC_FILE_READ_APDU_ERROR,None
        return 0,Data[2:apduLength*2-2]
    
    def __readICCInfos(self):
        #选择DF01
        ret,APDUList,Data,ReturnStatus = self.reader.HFCmd(1,"0700A40000021001")
        if ret!=0 or ReturnStatus!=0:return CETC_ICCTrader.READ_ICC_FILE_FAIL
        #读取0015文件
        ret,APDUList,Data,ReturnStatus = self.reader.HFCmd(1,"0500b095002b")
        res,fileData = self.__processFileReadResult(ret,APDUList,Data,ReturnStatus)
        if res !=0:return res 
        self.__process0015File(fileData)
        #读余额-0002文件
        ret,APDUList,Data,ReturnStatus = self.reader.HFCmd(1,"05805C000204")
        res,fileData = self.__processFileReadResult(ret,APDUList,Data,ReturnStatus)
        if res !=0:return res 
        self.__process0002File(fileData)
        #读上次过站信息-0019文件
        ret,APDUList,Data,ReturnStatus = self.reader.HFCmd(1,"0500B201cc2b")
        res,fileData = self.__processFileReadResult(ret,APDUList,Data,ReturnStatus)
        if res !=0:return res 
        self.__process0019File(fileData)
        return 0
    
    def __process0015File(self,dataFile):   #TODO这里面都没进行类型转换呢，后面根据需要逐步扩
        self.currentIcc["icc_card_provider"] = dataFile[0:8]*2
        self.currentIcc["cardType"] = dataFile[16:18]
        self.currentIcc["cardVersion"] = dataFile[18:20]
        self.currentIcc["cardNetId"] = dataFile[20:24]
        self.currentIcc["cpuCardInnerId"] = dataFile[24:40] #就是光哥代码中的icc_card_sn
        self.currentIcc["icc_card_sn"] = dataFile[24:40]
        self.currentIcc["validTime"] = dataFile[40:48]
        self.currentIcc["expireTime"] = dataFile[48:56]
        self.currentIcc["vehicleLicencePlateNumber"] = dataFile[56:80]
        self.currentIcc["useType"] = dataFile[80:82]
        #self.currentIcc["icc_card_sn"] = dataFile[24:40]
    
    def __process0002File(self,dataFile):
        self.currentIcc["cardRestMoney"] = int(dataFile,16) #卡余额，单位：分
        
    def __process0019File(self,dataFile):
        self.currentIccLastStation["roadNetId"] = dataFile[6:10]
        self.currentIccLastStation["stationId"] = dataFile[10:14]
        self.currentIccLastStation["laneId"] = dataFile[14:16]
        self.currentIccLastStation["passTime"] = dataFile[16:24]
        self.currentIccLastStation["vehicleType"] = dataFile[24:26]
        self.currentIccLastStation["state"] = dataFile[26:28]
        self.currentIccLastStation["tollCollectorId"] = dataFile[46:52]
        self.currentIccLastStation["classOrder"] = dataFile[52:54]
        self.currentIccLastStation["vehicleLicencePlateNumber"] = dataFile[54:78]
        
        
        

#---------------------------------------以下测试-----------------------------------------------
from PyQt4 import QtGui,QtCore
from PyQt4.QtGui import QMessageBox
import sys,os
QtGui.QApplication.setStyle("cleanlooks")
app = QtGui.QApplication( sys.argv )
 
class TestMainWnd(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setWindowTitle(u"车位管理测试容器")
        self.slotFrameLayout = QtGui.QHBoxLayout()
        self.setLayout(self.slotFrameLayout)
        
        self.readiccBtn = QtGui.QPushButton(u"读取ICC",self)
        self.slotFrameLayout.addWidget(self.readiccBtn)
        self.connect(self.readiccBtn,QtCore.SIGNAL("clicked()"),self.__readicc)
        
        self.tollBtn = QtGui.QPushButton(u"扣费",self)
        self.slotFrameLayout.addWidget(self.tollBtn)
        self.connect(self.tollBtn,QtCore.SIGNAL("clicked()"),self.__toll)
        
        
        self.issuer = KchtCpuCardIssuerTrader(u"发卡器思密达",{u"路网编号":"3232",u"路公司编号":"1122",u"业主编号":"2233",u"站编号":"3535",
                                               u"广场号":"12",u"车道编号":"01",
                                               u"PSAM卡槽号":"1"})

    def closeEvent(self,evt):
        os._exit(0)
    
    def __readicc(self):
        icc,iccStation = self.issuer.readICCInfo()
        print icc,iccStation
        
    def __toll(self):
        print "readICC res=",self.issuer.readICCInfo()
        print "toll res=",self.issuer.tollOnExit(1)
        



if __name__ == '__main__':
    wnd = TestMainWnd()
    wnd.show()
    
    app.exec_()
    


        
        
        
        
        
        