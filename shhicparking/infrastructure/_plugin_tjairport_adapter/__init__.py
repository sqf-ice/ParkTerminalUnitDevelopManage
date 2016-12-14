#encoding:utf-8

print 'ETC infrastructures initialized for Tianjin Binhai International Airport'

from shhicparking.infrastructure.pluginHelper import registerInfrasCls,registerInfrasProps

from LaneIODevice import LaneIODevice
from LaneLedIntegratedDevice import LaneLedIntegratedDevice
from KchtCpuCardIssuerTrader import KchtCpuCardIssuerTrader
from JuliLaneRsuIntegratedIntf import JuliLaneRsuIntegratedIntf
from TjdCamera import TjdCamera

registerInfrasCls(u"车道IO设备",LaneIODevice)
registerInfrasCls(u"聚力RSU集成接口设备",JuliLaneRsuIntegratedIntf)
registerInfrasCls(u"科畅慧通IC卡交易设备",KchtCpuCardIssuerTrader)
registerInfrasCls(u"车道LED显示屏一体机",LaneLedIntegratedDevice)
registerInfrasCls(u"停简单摄像头",TjdCamera)

registerInfrasProps(u"车道IO设备",[u"触发线圈输入端子",u"存在线圈输入端子",u"停止线圈输入端子",u"雨棚灯控制端子",u"道闸抬起控制端子",u"道闸落下控制端子"])
registerInfrasProps(u"聚力RSU集成接口设备",[u"设备串口号",u"路网编号",u"路公司编号",u"业主编号",u"站编号",u"广场号",u"车道编号"])
registerInfrasProps(u"科畅慧通IC卡交易设备",[u"路网编号",u"路公司编号",u"业主编号",u"站编号",u"广场号",u"车道编号",u"PSAM卡槽号"])
registerInfrasProps(u"车道LED显示屏一体机",[u"设备串口号",u"空闲消息"])
registerInfrasProps(u"停简单摄像头",[u"设备IP",u"端口号",u"用户名",u"密码",u"VLC驱动路径"])

#以下用于测试的部分桩
import shhicparking.infrastructure._plugin_mock_complex_etc_adapter


