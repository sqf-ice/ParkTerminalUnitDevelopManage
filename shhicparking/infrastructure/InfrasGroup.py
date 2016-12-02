#encoding:utf-8
'''
Created on 2015-6-9

出入口设施组

一个设施组中含有全部的设施，其中可能有空实现；

@author: user
'''
from OptionalInfrastructures import PesudoOptionalInfrastructures

class InfrasGroup:
    '''出入口设施组'''
    def __init__(self,infrasGroupId,infrasGroupElt):
        '''初始化，传入参数:基础设施ID，基础设施XML元素'''
        self.infrasGroupId = infrasGroupId
        self.pathType = infrasGroupElt.attr("pathType")    #设施组（出入口）类型
        self.uiType = infrasGroupElt.attr("uiType") if infrasGroupElt.attr("uiType") != "" else "common"
        self.relatedEntryIds = infrasGroupElt.attr("relatedEntryIds").split(",") \
            if infrasGroupElt.attr("relatedEntryIds") != "" else []
        self.passStrategy = infrasGroupElt.attr("passStrategy")
        
        self.infras = {}
        self.infrasImpl = []
        self.optionsInfras = PesudoOptionalInfrastructures()    #伪设施，用于没有配置的设施
        
    def addInfras(self,infrs):
        '''添加设施'''
        self.infrasImpl.append(infrs)
        for role in infrs.getRoles():
            self.infras[role] = infrs
    
    def __str__(self):
        return '[InfrasGroup for %s,with id = %s]'%(self.pathType,self.infrasGroupId)

    def __getitem__(self,role):
        if role in self.infras:return self.infras[role]
        else:return self.optionsInfras
        
    def __contains__(self,role):
        return role in self.infras















