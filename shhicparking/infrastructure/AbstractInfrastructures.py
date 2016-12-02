# encoding:utf-8
'''
Created on 2015-6-9

抽象的基础设施基类，定义各个设施适配实现必须具备的接口
所有具体的设施实现必须继承自相应的基类
对于具体实现来说，可能某个设备同时实现多个基类

设施组中的设施包括（与相应的接口基类的名称相同）：
GroundSensingCoil_first
GroundSensingCoil_second
GroundSensingCoil_third
GroundSensingCoil_lock
ManualControlledVehicleComes
Camera
PhotoCapture
PlatePhotoParser
Guardrail
FrontendEtc
Speaker
LED
LotDetectorGroup
POS

@author: user
'''


class AbstractInfrastructure:
    '''基础设施基类，具体实现必须调用本基类的__init__方法'''

    def __init__(self, infrasId, props):
        self.infrasId = infrasId
        self.props = props

    def getRoles(self):
        '''获得该基础设施承载的角色列表，返回是一个[str,..]'''
        return filter(lambda x: x != 'AbstractInfrastructure', map(lambda x: x.__name__, self.__class__.__bases__))

    def getStatus(self):
        '''获得设备状态，如果设备不在线，返回None'''
        return u"正常"


class GroundSensingCoil_first:
    '''地感线圈-前级'''

    def vehicleOnFirstCoil(self):
        '''线圈上是否有车，返回bool'''
        raise Exception("No implement for GroundSensingCoil_before")


class GroundSensingCoil_second:
    '''地感线圈-中级'''

    def vehicleOnSecondCoil(self):
        '''线圈上是否有车，返回bool'''
        raise Exception("No implement for GroundSensingCoil_middle")


class GroundSensingCoil_third:
    '''地感线圈-后级'''

    def vehicleOnThirdCoil(self):
        '''线圈上是否有车，返回bool'''
        raise Exception("No implement for GroundSensingCoil_third")


class ManualControlledVehicleComes:
    '''用于人工控制的车辆到来，在地感硬件失效时，可以通过此控制来实现车辆出入场'''

    def isManualControlAllowed(self):
        '''是否允许人工控制'''
        raise Exception("No implement for ManualControlledVehicleComes")

    def manualAssertVehicleComes(self):
        '''人工设定车辆到来'''
        raise Exception("No implement for ManualControlledVehicleComes")


class GroundSensingCoil_lock:
    '''地感线圈-道闸过后的锁'''

    # 当出入口共用时，入场或出场的车辆在进入或退出后，会压到出场或入场的抓拍线圈
    # 为避免这种情况引发错误的出入场逻辑，通过此设施进行锁定
    def lockOppositeCoil(self):
        '''锁定对方线圈一段时间'''
        raise Exception("No implement for GroundSensingCoil_lock")

    def notifyCoilLock(self):
        '''别的线圈通过此方法来通知自己锁定'''
        raise Exception("No implement for GroundSensingCoil_lock")


class Camera:
    '''摄像头'''

    def startVedio(self, uiFrame):
        '''开始视频'''
        raise Exception("No implement for Camera")

    def stopVedio(self):
        '''结束视频'''
        raise Exception("No implement for Camera")


class PhotoCapture:
    '''图像抓拍器'''

    def capturePhoto(self):
        '''触发抓拍'''
        raise Exception("No implement for PhotoCapture")


class PlatePhotoParser:
    '''号牌识别器'''

    def parsePlateNo(self, photo=None):
        '''号牌识别，返回车牌和车型，入参可能是图片，也可能空（硬识别）'''
        pass


class RfidReader:
    '''RFID电子牌读写器'''

    def startRead(self):
        '''开始读取'''
        pass

    def stopRead(self):
        '''结束读取'''
        pass

    def getAllTags(self):
        '''获得从开始到结束中间所有读到的标签和车型，返回[车牌号列表],[车型列表]，两者一一对应'''
        raise Exception("No implement for RfidReader")


class Guardrail:
    '''进出栏杆'''

    def liftTheRail(self):
        '''抬杆'''
        raise Exception("No implement for Guardrail")

    def dropTheRail(self):
        '''落杆'''
        raise Exception("No implement for Guardrail")


class Speaker:
    '''扬声器'''

    def speak(self, message):
        '''说话'''
        raise Exception("No implement for Speaker")


class LED:
    '''LED提示器'''

    def showOnLed(self, message):
        '''LED上显示消息'''
        raise Exception("No implement for LED")

    def showIdleMsgOnLed(self):
        '''LED上显示默认空闲消息'''  # 可由子类重写，也可以不实现
        self.showOnLed(u"")


class POS:
    '''POS机'''

    def setConsumeType(self, consumeType):
        '''设置支付方式，1-普通插卡，2-QuickPass'''
        raise Exception("No implement for POS")

    def startConsume(self, fee):
        '''开始消费-指定消费金额'''
        raise Exception("No implement for POS")

    def tollFinished(self):
        '''询问是否消费完成，消费成功返回1，消费失败返回-1,尚未消费返回0'''
        raise Exception("No implement for POS")

    def getMessage(self):
        '''返回扣款信息'''
        return ""


class ParkingFeeCalculator:
    '''停车费计算器'''

    # 停车费计算器一般不是硬件，但也作为基础设施，可以插件化适配
    def getCurrentTollDetailTable(self):
        '''获取当前计费明细表'''  # 格式：[[开始时间,结束时间,计费方式,费率,金额],]
        raise Exception("No implement for ParkingFeeCalculator")

    def getCurrentSum(self):
        '''获得当前计算金额数'''
        raise Exception("No implement for ParkingFeeCalculator")

    def reloadScript(self):
        '''重新载入计费脚本'''
        raise Exception("No implement for ParkingFeeCalculator")

    def getScriptFile(self):
        '''获取计费脚本文件'''
        raise Exception("No implement for ParkingFeeCalculator")

    def calcActualParkingTimeAndFee(self, vehicleType, enterTime, exitTime, monthlyPayTimeInterval):
        '''计费并返回结果，返回值包含交易使用类型（错时停车、车位租赁，或""），及金额。'''
        # 入参enterTime,exitTime为毫秒时间戳
        # monthlyPayTimeInterval，车辆包月（错时停车）数据，格式为[[开始日期,结束日期,开始时间(距当天毫秒),结束时间],]
        raise Exception("No implement for ParkingFeeCalculator")

    def calcFee(self, vehicleType, parkingTime, exitTime):
        '''计算停车费，入参为车型及停车时间，出场时间'''
        return self.calcActualParkingTimeAndFee(vehicleType, exitTime - parkingTime, exitTime, [])[1]


class WhitelistProcessor:
    '''白名单处理者'''

    # 白名单处理者一般不是硬件，但也作为基础设施，可以插件化适配
    def checkFreeVehicle(self, plateNo, vehicleType, channelId):
        '''检查是否为白名单车辆，返回{"rtnCode":1,"info":....}'''
        # 若为可以自动放行，返回rtnCode = 1；若非自动放行白名单，返回2，非白名单返回0，info为信息
