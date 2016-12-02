#encoding:utf-8

'''

停车场基础设施适配

具体实现以插件形式放置在本包内，插件包的命名必须以plugin_开头
插件包的__init__.py中应调用registerInfras方法注册每个设施的具体实现类

'''

import os
from shhicparking.util.simplexml import xmldoc
from InfrasGroup import InfrasGroup
from pluginHelper import INFRAS_CLS
from shhicparking import SESSION
from shhicparking.server import TSStub

INFRAS_CONFIG_FILE = None

infrasPath = os.path.realpath(__file__)[:-len("__init__.py")-1]
for plugin in filter(lambda dirname:dirname.startswith('plugin_'),os.listdir(infrasPath)):
    exec("import shhicparking.infrastructure.%s"%plugin)
    global INFRAS_CONFIG_FILE
    INFRAS_CONFIG_FILE =  "shhicparking/infrastructure/"+plugin+"/InfrastructureConfig.xml"
    break

INFRAS_GROUPS = {}  #基础设施组组，key为组ID，value为InfrasGroup对象

def initInfras():
    '''初始化所有基础设施，由主函数调用'''
    global INFRAS_GROUPS,INFRAS_CLS,INFRAS_CONFIG_FILE
    configXml = xmldoc(INFRAS_CONFIG_FILE)
    g = configXml["parkingInfrasGroups"]["infrasGroup"]
    if not isinstance(g,list):g = [g]
    for infrasGroup in g:
        infrasGroupId = infrasGroup.attr("id")
        INFRAS_GROUPS[infrasGroupId] = InfrasGroup(infrasGroupId,infrasGroup)
        
        i = infrasGroup["infras"]
        if not isinstance(i,list):i = [i]
        for infras in i :
            infrasId = infras.attr("id")
            infrasType = infras.attr("infrasType")
            use = infras.attr("use")
            if use == 'false':continue
            props = {}
            p = infras["property"]
            if isinstance(p,list):
                for pi in p:
                    props[pi.attr("name")] = pi.value
            else:
                props[p.attr("name")] = p.value
            try:
                infrasImpl = INFRAS_CLS[infrasType](infrasId,props) #这里生成一个设施类了
                SESSION["mainWnd"].log(msg=u'初始化插件:['+infrasId+"]完成")
                INFRAS_GROUPS[infrasGroupId].addInfras(infrasImpl)
            except Exception,e:
                SESSION["mainWnd"].log(msg=u'初始化插件:['+infrasId+"]失败:"+str(e))
            
            
def getAllLocalChannels():
    #获得所有的本地车道名称
    res = TSStub.getAllInnerParkTerminal({})
    channels = []
    for a in res:
        if a[2] != "":channels.extend(a[2].split(","))
        if a[3] != "":channels.extend(a[3].split(","))
    channels.sort()
    return channels
