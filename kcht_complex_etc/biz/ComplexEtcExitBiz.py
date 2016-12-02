#encoding:utf-8
'''
Created on 2016-9-19
复杂高速ETC车道，出口逻辑
@author: zws
'''

from AbstractComplexEtcBiz import AbstractComplexEtcChannel

class ComplexEtcExitBiz(AbstractComplexEtcChannel):
    def __init__(self,infrasGroup,uiFrame):
        AbstractComplexEtcChannel.__init__(self,infrasGroup,uiFrame)
