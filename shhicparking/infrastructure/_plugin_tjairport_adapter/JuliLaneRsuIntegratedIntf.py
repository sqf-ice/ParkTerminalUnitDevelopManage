#encoding:utf-8
'''
Created on 2016-11-23
聚力车道RSU集成接口（天津地区）驱动
@author: kcht
'''
from shhicparking.infrastructure.AbstractInfrastructures import *
from kcht_complex_etc.infras import FrontendEtc

class JuliLaneRsuIntegratedIntf(AbstractInfrastructure,FrontendEtc):
    def __init__(self,infrasId,props):
        AbstractInfrastructure.__init__(self, infrasId, props)
        self.stationInfo = {"roadNetworkId":props[u"路网编号"],"roadCompanyId":props[u"路公司编号"]
                            ,"ownerId":props[u"业主编号"],"stationId":props[u"站编号"]
                            ,"areaId":props[u"广场号"],"channelId":props[u"车道编号"]} 


    def getStationInfo(self):
        "获得站级的信息"
        #返回值应包含：{"roadNetworkId":"路网编号","roadCompanyId":"路公司编号","ownerId":"业主编号","stationId":"站编号","areaId":"广场号","channelId":"车道编号"} 
        return self.stationInfo 

    def notifyEntry(self,entryId = None,enterTime = None,plateNo=None,vehicleType=None):
        raise Exception("No implement for FrontendEtc")
    
    def tollOnExit(self,info,exitId = None,exitTime = None,plateNo=None,vehicleType=None):
        raise Exception("No implement for FrontendEtc")
   
    def getMessage(self):
        "返回当前消息"
        raise Exception("No implement for FrontendEtc")
    
    
    
    