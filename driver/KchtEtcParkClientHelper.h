


#include "../rsuTradeHelper/rsuTradeDataStructs.h"

extern "C"{
	/*
		注册RSU设备
		入参:
			device:设备串口号，或者设备IP地址
			initRequest:初始化设备请求
			initResult:（出参）初始化设备返回，携带设备基本信息
		返回值:
			错误码，详见头文件中定义的宏
	*/
	_declspec(dllexport) int _cdecl KTRSU_registerRsu(const char* device,StationRegisterInfo* stationRegisterInfo, InitialDeviceRequest* initRequest, InitialDeviceResult* initResult);

	/*
		移除注册设备
		入参:
			device:设备串口号，或者设备IP地址
		返回值:
			错误码，详见头文件中定义的宏
	*/
	_declspec(dllexport) int _cdecl KTRSU_unregisterRsu(const char* device);

	/*
		更换班次
		入参：
			device:设备号
			staffInfo:班次信息
		返回值：
			错误码，详见头文件中定义的宏
	*/
	_declspec(dllexport) int _cdecl KTRSU_changeClassOrder(const char* device, StaffInfo *staffInfo);

	/*
		获得OBU车辆信息
		入参：
			device:设备标识
			vehicleInfo:（出参）车辆信息
			timeout:获取车辆属性的超时时间
			followTrade:是否有后续交易，如果为true必须有submitEntryTrading或submitExitTrading函数被调用，否则超时自动中止本次交易;
						为false则表明没有后续的交易。
		返回值:
			错误码，详见头文件中定义的宏
	*/
	_declspec(dllexport) int _cdecl KTRSU_getTradingVehicleInfo(const char* device,EtcVehicleInfo* vehicleInfo,int timeout,bool followTrade);

	/*
		入口交易
		入参：
			device:设备标识
			entryTradeInfo:入口交易命令
			entryTradeResult:（出参）入口交易结果
			timeout:交易超时时间
		返回值：
			错误码，详见头文件中定义的宏
	*/
	_declspec(dllexport) int _cdecl KTRSU_submitEntryTrading(const char* device, EntryTradeRequest* entryTradeRequest,EntryTradeResult* entryTradeResult,int timeout);

	/*
		出口交易
		入参：
			device:设备标识
			exitTradeRequest:出口交易命令
			exitTradeResult:（出参）出口交易结果
			timeout:交易超时时间
		返回值：
			错误码，详见头文件中定义的宏
	*/
	_declspec(dllexport) int _cdecl KTRSU_submitExitTrading(const char* device, ExitTradeRequest* exitTradeRequest, ExitTradeResult* exitTradeResult,  int timeout);

	/*
		解析0015文件到常用卡片发行信息数据结构
		入参：
			file0015：文件内容指针，从B4帧ISsuerInfo域获得
			info：（出参）解析后的数据结构
		返回值：
			可直接忽略
	*/
	_declspec(dllexport) int _cdecl KTRSU_parseICCIssuerInfo(char* file0015, ICCIssuerInfo* info);

	/*
		解析0019文件到常用过站信息数据结构
		入参：
			file0019：文件内容指针，从B4帧LastStation域获得
			info:（出参）解析后的数据结构
		返回值：
			可直接忽略
	*/
	_declspec(dllexport) int _cdecl KTRSU_parseStationPassInfo(char* file0019, StationPassInfo* info);

	/*
		注册ETC停车场中心服务
		入参：
			serverUrl：服务URL，格式：https://xxx.xxx.xx.xx:8443/ETCParkingFrontServiceWeb/service
			certFile：证书文件
		返回值：
			注册ETC服务结果
	*/
	_declspec(dllexport) int _cdecl KTSV_registerEtcServer(char* serverUrl, char* certFile);

	/*
		入场上报服务
		入参：
			vehicleInfo:OBU车辆信息，由KTRSU_getTradingVehicleInfo方法返回
			entryTradeResult:入口交易结果，由KTRSU_submitEntryTrading方法返回
			payloadJson:（出参）上报通知负载，指针由外部传入后，用于存储负载。
		返回值：
			上报结果，若结果失败，可暂存payloadJson串，后续通过KTSV_resendNotify方法重传
	*/
	_declspec(dllexport) int _cdecl KTSV_notifyEntry(EtcVehicleInfo* vehicleInfo, EntryTradeResult* entryTradeResult,char* payloadJson);

	/*
		出场上报服务
		入参：
			vehicleInfo：OBU车辆信息，由KTRSU_getTradingVehicleInfo方法返回
			dueToll：扣费金额
			exitTradeResult：出口交易结果，由KTRSU_submitExitTrading方法返回
			payloadJson：（出参）上报通知负载，指针由外部传入后，用于存储负载。
		返回值：
			上报结果，若结果失败，可暂存payloadJson串，后续通过KTSV_resendNotify方法重传
	*/
	_declspec(dllexport) int _cdecl KTSV_notifyExit(EtcVehicleInfo* vehicleInfo, int dueToll, ExitTradeResult* exitTradeResult,char* payloadJson);

	/*
		IC卡交易上报服务
		入参:
			obuid：obuid
			iccTradeInfo：IC卡交易信息
			payloadJson：（出参）上报通知负载，指针由外部传入后，用于存储负载。
		返回值：
			上报结果，若结果失败，可暂存payloadJson串，后续通过KTSV_resendNotify方法重传
	*/
	_declspec(dllexport) int _cdecl KTSV_notifyExitForICCTrade(char* obuid, ICCTradeInfo* iccTradeInfo, char* payloadJson);

	/*
		重传ETC交易服务负载
		入参：
			payloadJson:重传子串，由KTSV_notifyEntry,KTSV_notifyExit,KTSV_notifyExitForICCTrade方法返回
		返回值：
			上报结果，若结果失败，可暂存payloadJson串，后续通过KTSV_resendNotify方法重传
	*/
	_declspec(dllexport) int _cdecl KTSV_resendNotify(char* payloadJson);

	/*
		黑名单查询
		入参：
			vehicleInfo：车辆信息
			isBlacklist：（出参）是否是黑名单
		返回值：
			查询结果
	*/
	_declspec(dllexport) int _cdecl KTSV_etcBlacklistQuery(EtcVehicleInfo* vehicleInfo, int* isBlacklist);

}