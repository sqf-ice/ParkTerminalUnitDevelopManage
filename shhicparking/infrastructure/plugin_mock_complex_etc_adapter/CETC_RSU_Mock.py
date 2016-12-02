# encoding:utf-8
'''
Created on 2016-10-26

@author: user
'''

from shhicparking.infrastructure.AbstractInfrastructures import *
from kcht_complex_etc.infras import FrontendEtc


class CETC_RSU_Mock(AbstractInfrastructure, RfidReader, FrontendEtc):
    "打桩实现的RSU模块驱动"

    def __init__(self, infrasId, props):
        AbstractInfrastructure.__init__(self, infrasId, props)
        self.stationInfo = {"roadNetworkId": props[u"路网编号"], "roadCompanyId": props[u"路公司编号"]
            , "ownerId": props[u"业主编号"], "stationId": props[u"站编号"]
            , "areaId": props[u"广场号"], "channelId": props[u"车道编号"]}

    def getStationInfo(self):
        "获得站级的信息"
        # 返回值应包含：{"roadNetworkId":"路网编号","roadCompanyId":"路公司编号","ownerId":"业主编号","stationId":"站编号","areaId":"广场号","channelId":"车道编号"}
        return self.stationInfo

    def startRead(self):
        '''开始读取'''
        pass

    def stopRead(self):
        '''结束读取'''
        pass

    def getAllTags(self):
        '''获得从开始到结束中间所有读到的标签和车型，返回[车牌号列表],[车型列表]，两者一一对应'''
        raise Exception("No implement for RfidReader")

    def notifyEntry(self, entryId, enterTime, plateNo=None, vehicleType=None):
        "车辆进场时的收费初始化"  # 入参为车道、进入时间（毫秒戳），车牌号和车型可选，因为前端电子收费往往与电子识别一体
        # 设置不成功时抛出上面的相应异常
        raise Exception("No implement for FrontendEtc")

    def tollOnExit(self, info, exitId, exitTime, fee, plateNo=None, vehicleType=None):
        "车辆出场时收费"  # 入参为车道、出场时间（毫秒戳），收费金额。车牌号和车型可选，因为前端电子收费往往与电子识别一体
        # 设置不成功时抛出上面的相应异常
        raise Exception("No implement for FrontendEtc")

    def getMessage(self):
        "返回当前消息"
        raise Exception("No implement for FrontendEtc")
