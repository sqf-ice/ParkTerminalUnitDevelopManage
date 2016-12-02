# encoding:utf-8
"复杂ETC车道设备适配，这些设备适配与普通停车场不同，抽象也不同"

print 'mock complex etc infrastructure adapter import'

from shhicparking.infrastructure.pluginHelper import registerInfrasCls, registerInfrasProps

from CETC_Mocks import *
from CETC_RSU_Mock import CETC_RSU_Mock

registerInfrasCls(u"虚拟ETC6线圈地感", CETC_GroundCoils_Mock)
registerInfrasCls(u"虚拟ETC信号", CETC_Signals_Mock)
registerInfrasCls(u"虚拟ETC基础设施", CETC_Infras_Mock)
registerInfrasCls(u"虚拟RSU", CETC_RSU_Mock)

registerInfrasProps(u"虚拟ETC6线圈地感", ["noParam"])
registerInfrasProps(u"虚拟ETC信号", ["noParam"])
registerInfrasProps(u"虚拟ETC基础设施", ["noParam"])
registerInfrasProps(u"虚拟RSU", [u"路网编号", u"路公司编号", u"业主编号", u"站编号", u"广场号", u"车道编号"])
