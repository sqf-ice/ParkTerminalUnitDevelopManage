# encoding:utf-8
'''
Created on 2015-6-12

@author: user
'''

INFRAS_CLS = {}  # 基础设施实现类组，key为infrasType，value为实现类
INFRAS_PROPS = {}  # 基础设施参数组，key为infrasType，value为[参数列表]，所有参数均为str类型


def registerInfrasCls(infrasType, infrasCls):
    '''注册基础设施实现类，由插件的__init__中调用，从而实现对插件的解耦'''
    INFRAS_CLS[infrasType] = infrasCls


def registerInfrasProps(infrasType, propList):
    '''注册基础设施实现类的属性列表，由插件的__init__中调用，从而实现可视化的界面参数配置'''
    INFRAS_PROPS[infrasType] = propList
