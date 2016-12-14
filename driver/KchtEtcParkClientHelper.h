


#include "../rsuTradeHelper/rsuTradeDataStructs.h"

extern "C"{
	/*
		ע��RSU�豸
		���:
			device:�豸���ںţ������豸IP��ַ
			initRequest:��ʼ���豸����
			initResult:�����Σ���ʼ���豸���أ�Я���豸������Ϣ
		����ֵ:
			�����룬���ͷ�ļ��ж���ĺ�
	*/
	_declspec(dllexport) int _cdecl KTRSU_registerRsu(const char* device,StationRegisterInfo* stationRegisterInfo, InitialDeviceRequest* initRequest, InitialDeviceResult* initResult);

	/*
		�Ƴ�ע���豸
		���:
			device:�豸���ںţ������豸IP��ַ
		����ֵ:
			�����룬���ͷ�ļ��ж���ĺ�
	*/
	_declspec(dllexport) int _cdecl KTRSU_unregisterRsu(const char* device);

	/*
		�������
		��Σ�
			device:�豸��
			staffInfo:�����Ϣ
		����ֵ��
			�����룬���ͷ�ļ��ж���ĺ�
	*/
	_declspec(dllexport) int _cdecl KTRSU_changeClassOrder(const char* device, StaffInfo *staffInfo);

	/*
		���OBU������Ϣ
		��Σ�
			device:�豸��ʶ
			vehicleInfo:�����Σ�������Ϣ
			timeout:��ȡ�������Եĳ�ʱʱ��
			followTrade:�Ƿ��к������ף����Ϊtrue������submitEntryTrading��submitExitTrading���������ã�����ʱ�Զ���ֹ���ν���;
						Ϊfalse�����û�к����Ľ��ס�
		����ֵ:
			�����룬���ͷ�ļ��ж���ĺ�
	*/
	_declspec(dllexport) int _cdecl KTRSU_getTradingVehicleInfo(const char* device,EtcVehicleInfo* vehicleInfo,int timeout,bool followTrade);

	/*
		��ڽ���
		��Σ�
			device:�豸��ʶ
			entryTradeInfo:��ڽ�������
			entryTradeResult:�����Σ���ڽ��׽��
			timeout:���׳�ʱʱ��
		����ֵ��
			�����룬���ͷ�ļ��ж���ĺ�
	*/
	_declspec(dllexport) int _cdecl KTRSU_submitEntryTrading(const char* device, EntryTradeRequest* entryTradeRequest,EntryTradeResult* entryTradeResult,int timeout);

	/*
		���ڽ���
		��Σ�
			device:�豸��ʶ
			exitTradeRequest:���ڽ�������
			exitTradeResult:�����Σ����ڽ��׽��
			timeout:���׳�ʱʱ��
		����ֵ��
			�����룬���ͷ�ļ��ж���ĺ�
	*/
	_declspec(dllexport) int _cdecl KTRSU_submitExitTrading(const char* device, ExitTradeRequest* exitTradeRequest, ExitTradeResult* exitTradeResult,  int timeout);

	/*
		����0015�ļ������ÿ�Ƭ������Ϣ���ݽṹ
		��Σ�
			file0015���ļ�����ָ�룬��B4֡ISsuerInfo����
			info�������Σ�����������ݽṹ
		����ֵ��
			��ֱ�Ӻ���
	*/
	_declspec(dllexport) int _cdecl KTRSU_parseICCIssuerInfo(char* file0015, ICCIssuerInfo* info);

	/*
		����0019�ļ������ù�վ��Ϣ���ݽṹ
		��Σ�
			file0019���ļ�����ָ�룬��B4֡LastStation����
			info:�����Σ�����������ݽṹ
		����ֵ��
			��ֱ�Ӻ���
	*/
	_declspec(dllexport) int _cdecl KTRSU_parseStationPassInfo(char* file0019, StationPassInfo* info);

	/*
		ע��ETCͣ�������ķ���
		��Σ�
			serverUrl������URL����ʽ��https://xxx.xxx.xx.xx:8443/ETCParkingFrontServiceWeb/service
			certFile��֤���ļ�
		����ֵ��
			ע��ETC������
	*/
	_declspec(dllexport) int _cdecl KTSV_registerEtcServer(char* serverUrl, char* certFile);

	/*
		�볡�ϱ�����
		��Σ�
			vehicleInfo:OBU������Ϣ����KTRSU_getTradingVehicleInfo��������
			entryTradeResult:��ڽ��׽������KTRSU_submitEntryTrading��������
			payloadJson:�����Σ��ϱ�֪ͨ���أ�ָ�����ⲿ��������ڴ洢���ء�
		����ֵ��
			�ϱ�����������ʧ�ܣ����ݴ�payloadJson��������ͨ��KTSV_resendNotify�����ش�
	*/
	_declspec(dllexport) int _cdecl KTSV_notifyEntry(EtcVehicleInfo* vehicleInfo, EntryTradeResult* entryTradeResult,char* payloadJson);

	/*
		�����ϱ�����
		��Σ�
			vehicleInfo��OBU������Ϣ����KTRSU_getTradingVehicleInfo��������
			dueToll���۷ѽ��
			exitTradeResult�����ڽ��׽������KTRSU_submitExitTrading��������
			payloadJson�������Σ��ϱ�֪ͨ���أ�ָ�����ⲿ��������ڴ洢���ء�
		����ֵ��
			�ϱ�����������ʧ�ܣ����ݴ�payloadJson��������ͨ��KTSV_resendNotify�����ش�
	*/
	_declspec(dllexport) int _cdecl KTSV_notifyExit(EtcVehicleInfo* vehicleInfo, int dueToll, ExitTradeResult* exitTradeResult,char* payloadJson);

	/*
		IC�������ϱ�����
		���:
			obuid��obuid
			iccTradeInfo��IC��������Ϣ
			payloadJson�������Σ��ϱ�֪ͨ���أ�ָ�����ⲿ��������ڴ洢���ء�
		����ֵ��
			�ϱ�����������ʧ�ܣ����ݴ�payloadJson��������ͨ��KTSV_resendNotify�����ش�
	*/
	_declspec(dllexport) int _cdecl KTSV_notifyExitForICCTrade(char* obuid, ICCTradeInfo* iccTradeInfo, char* payloadJson);

	/*
		�ش�ETC���׷�����
		��Σ�
			payloadJson:�ش��Ӵ�����KTSV_notifyEntry,KTSV_notifyExit,KTSV_notifyExitForICCTrade��������
		����ֵ��
			�ϱ�����������ʧ�ܣ����ݴ�payloadJson��������ͨ��KTSV_resendNotify�����ش�
	*/
	_declspec(dllexport) int _cdecl KTSV_resendNotify(char* payloadJson);

	/*
		��������ѯ
		��Σ�
			vehicleInfo��������Ϣ
			isBlacklist�������Σ��Ƿ��Ǻ�����
		����ֵ��
			��ѯ���
	*/
	_declspec(dllexport) int _cdecl KTSV_etcBlacklistQuery(EtcVehicleInfo* vehicleInfo, int* isBlacklist);

}