#pragma once

#define	SUCCESS 0

#define PARAM_ERROR	-1001		//参数错误

#define DEVICE_PORT_OPEN_FAIL	-2001	//设备端口打开失败
#define DEVICE_NOT_REGISTERED	-2002	//设备未注册
#define DEVICE_CMD_SEND_FAIL -2003	//设备命令发送失败
#define DEVICE_NOT_RESPONSE -2004	//设备没有响应

#define NO_OBU_FOUND	-3001	//没有OBU
#define OBU_DSRC_ERROR	-3002	//OBU通信异常

#define RSU_CMD_ERROR	-4001	//RSU指令执行错误，例如指令顺序错误等

//站级注册信息
struct StationRegisterInfo{
	char roadNetId[2];	//入口收费路网号
	char stationId[2];	//入口收费站号
	char laneId;	//入口收费车道号
	char entryOrExit;	//出入口标识：01-MTC入口，02-MTC出口，03-ETC入口，04-ETC出口
};

//班次，收费员信息
struct StaffInfo{
	char tollCollectorId[3];	//收费员工号
	char classOrder;	//班次号
};

//设备初始化命令
struct InitialDeviceRequest{
	char laneMode;	//车道模式，取值为3/4/6/7/8
	char waitTime;	//最小重读时间
	char txPower;	//功率技术
	char pllChannelId;	//信道号
	char transClass;	//交易模式：0-记账卡和储值卡都是传统交易，1-记账卡和储值卡都是复合消费，2-记账卡是传统交易，储值卡是复合交易
};

//设备初始化结果
struct InitialDeviceResult{
	char rsuStatus;	//主状态，00-正常，其他表示异常
	char psamNum;	//PSAM卡个数
	char rsuTerminalId1[6];	//PSAM卡1终端机编号
	char rsuTerminalId2[6];	//PSAM卡2终端机编号
	char rsuAlgId;	//算法标识
	char rsuManuId[2];	//RSU厂商代码，16进制表示
	char rsuId[2];	//RSU编号，16进制表示
	char rsuVersion[2];	//RSU软件版本号
};

//车辆信息结构
struct EtcVehicleInfo{
	char obuid[4];	//OBUID
	char issuerIdentifier[8];	//发行商代码
	char serialNumber[8];	//应用序列号
	char dateOfIssue[4];	//启用日期
	char dateOfExpire[4];	//过期日期
	char equipmentsStatus;	//设备类型
	
	char iccExists;	//IC卡是否存在，0-存在，1-无IC卡
	char surfaceType;	//界面类型：0-接触式界面，1-非接触式界面
	char iccType;	//卡类型，0-CPU卡
	char iccStatus;	//IC卡状态，0-正常，1-出错
	char locked;	//OBU锁定状态，0-未锁定，1-被锁定
	char disassemble;	//拆卸状态：0-未拆卸，1-被拆卸
	char battaryStatus;	//电池状态，0-正常，1-电量低

	char vehicleLicencePlateNumber[12];	//车牌号
	char vehicleLicencePlateColor[2];	//车牌颜色
	char vehicleClass;	//车辆类型
	char vehicleUserType;	//车辆用户类型

	char cardType;	//卡类型，00-国标，其他保留
	char physicalCardType;	//物理卡类型
	char transType;	//交易类型，0x00-传统交易，0x10-复合交易
	int cardRestMoney;	//卡余额，单位：分
	char cardId[4];	//物理卡号
	char issuerInfo[43];	//卡发行信息
	char lastStation[40]; //上次过站信息
	int stationLen;//过站信息文件长度
};


//入口交易命令
struct EntryTradeRequest{
	char obuid[4];	//OBUID
	char transSerial[4];	//交易顺序号，自行分配
};

//入口交易结果
struct EntryTradeResult{
	char obuid[4];	//OBUID
	char tradeResult;	//交易状态	0-交易成功，1-交易失败
	long wrFileTime;	//写文件时间
	char psamNo[6];	//PSAM卡终端机编号
	char psamTransSerial[4];	//PSAM卡交易序号
	char tac[4];	//TAC
	StationRegisterInfo stationRegisterInfo;	//当前站信息
	StaffInfo staffInfo;
};

//出口交易命令
struct ExitTradeRequest{
	char obuid[4];	//OBUID
	char transSerial[4];	//交易顺序号，自行分配
	int consumeMoney;	//扣款额度
};

//出口交易结果
struct ExitTradeResult{
	char obuid[4];	//OBUID
	char tradeResult;	//交易状态	0-交易成功，非0-交易失败
	long wrFileTime;	//写文件时间
	char psamNo[6];	//PSAM卡终端机编号
	char transTime[7];	//交易时间，格式YYYYMMDDHHMMSS
	char transType;	//交易类型
	char tac[4];	//TAC
	char iccPaySerial[2];	//CPU卡交易序号
	char psamTransSerial[4];	//PSAM卡交易序号
	int cardBalance;	//交易后余额，如果读取余额失败，返回负数
	StationRegisterInfo stationRegisterInfo;
	StaffInfo staffInfo;
};

//过站信息-只取常用的
struct StationPassInfo{
	char roadNetId[2];	//路网编号
	char stationId[2];	//收费站编号
	char laneId;	//车道号
	long passTime;	//通过时间-UNIX时间
	char vehicleType;	//车型
	char state;	//出入口状态，01-MTC入口，02-MTC出口
	char tollCollectorId[3];	//收费员工号
	char classOrder;	//班次
	char vehicleLicencePlateNumber[12];	//车牌号
};

//IC卡片发行信息-只取常用的
struct ICCIssuerInfo{
	char cardType;	//卡片类型：22-储值卡，23-记账卡
	char cardNetId[2];	//卡片网络编号
	char cpuCardInnerId[8];	//CPU卡内部编号
};

//IC卡交易信息
struct ICCTradeInfo{
	char etcPsamId[6];
	char etcPsamTradeNum[4];
	char tacCode[4];
	long dueToll;	//应扣款
	long balanceBeforeTrade;	//交易前余额
	long balanceAfterTrade;	//交易后余额
	StationPassInfo entryStationInfo;
	StationPassInfo exitStationInfo;
	ICCIssuerInfo iccInfo;
};