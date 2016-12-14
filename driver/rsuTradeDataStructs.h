#pragma once

#define	SUCCESS 0

#define PARAM_ERROR	-1001		//��������

#define DEVICE_PORT_OPEN_FAIL	-2001	//�豸�˿ڴ�ʧ��
#define DEVICE_NOT_REGISTERED	-2002	//�豸δע��
#define DEVICE_CMD_SEND_FAIL -2003	//�豸�����ʧ��
#define DEVICE_NOT_RESPONSE -2004	//�豸û����Ӧ

#define NO_OBU_FOUND	-3001	//û��OBU
#define OBU_DSRC_ERROR	-3002	//OBUͨ���쳣

#define RSU_CMD_ERROR	-4001	//RSUָ��ִ�д�������ָ��˳������

//վ��ע����Ϣ
struct StationRegisterInfo{
	char roadNetId[2];	//����շ�·����
	char stationId[2];	//����շ�վ��
	char laneId;	//����շѳ�����
	char entryOrExit;	//����ڱ�ʶ��01-MTC��ڣ�02-MTC���ڣ�03-ETC��ڣ�04-ETC����
};

//��Σ��շ�Ա��Ϣ
struct StaffInfo{
	char tollCollectorId[3];	//�շ�Ա����
	char classOrder;	//��κ�
};

//�豸��ʼ������
struct InitialDeviceRequest{
	char laneMode;	//����ģʽ��ȡֵΪ3/4/6/7/8
	char waitTime;	//��С�ض�ʱ��
	char txPower;	//���ʼ���
	char pllChannelId;	//�ŵ���
	char transClass;	//����ģʽ��0-���˿��ʹ�ֵ�����Ǵ�ͳ���ף�1-���˿��ʹ�ֵ�����Ǹ������ѣ�2-���˿��Ǵ�ͳ���ף���ֵ���Ǹ��Ͻ���
};

//�豸��ʼ�����
struct InitialDeviceResult{
	char rsuStatus;	//��״̬��00-������������ʾ�쳣
	char psamNum;	//PSAM������
	char rsuTerminalId1[6];	//PSAM��1�ն˻����
	char rsuTerminalId2[6];	//PSAM��2�ն˻����
	char rsuAlgId;	//�㷨��ʶ
	char rsuManuId[2];	//RSU���̴��룬16���Ʊ�ʾ
	char rsuId[2];	//RSU��ţ�16���Ʊ�ʾ
	char rsuVersion[2];	//RSU����汾��
};

//������Ϣ�ṹ
struct EtcVehicleInfo{
	char obuid[4];	//OBUID
	char issuerIdentifier[8];	//�����̴���
	char serialNumber[8];	//Ӧ�����к�
	char dateOfIssue[4];	//��������
	char dateOfExpire[4];	//��������
	char equipmentsStatus;	//�豸����
	
	char iccExists;	//IC���Ƿ���ڣ�0-���ڣ�1-��IC��
	char surfaceType;	//�������ͣ�0-�Ӵ�ʽ���棬1-�ǽӴ�ʽ����
	char iccType;	//�����ͣ�0-CPU��
	char iccStatus;	//IC��״̬��0-������1-����
	char locked;	//OBU����״̬��0-δ������1-������
	char disassemble;	//��ж״̬��0-δ��ж��1-����ж
	char battaryStatus;	//���״̬��0-������1-������

	char vehicleLicencePlateNumber[12];	//���ƺ�
	char vehicleLicencePlateColor[2];	//������ɫ
	char vehicleClass;	//��������
	char vehicleUserType;	//�����û�����

	char cardType;	//�����ͣ�00-���꣬��������
	char physicalCardType;	//��������
	char transType;	//�������ͣ�0x00-��ͳ���ף�0x10-���Ͻ���
	int cardRestMoney;	//������λ����
	char cardId[4];	//������
	char issuerInfo[43];	//��������Ϣ
	char lastStation[40]; //�ϴι�վ��Ϣ
	int stationLen;//��վ��Ϣ�ļ�����
};


//��ڽ�������
struct EntryTradeRequest{
	char obuid[4];	//OBUID
	char transSerial[4];	//����˳��ţ����з���
};

//��ڽ��׽��
struct EntryTradeResult{
	char obuid[4];	//OBUID
	char tradeResult;	//����״̬	0-���׳ɹ���1-����ʧ��
	long wrFileTime;	//д�ļ�ʱ��
	char psamNo[6];	//PSAM���ն˻����
	char psamTransSerial[4];	//PSAM���������
	char tac[4];	//TAC
	StationRegisterInfo stationRegisterInfo;	//��ǰվ��Ϣ
	StaffInfo staffInfo;
};

//���ڽ�������
struct ExitTradeRequest{
	char obuid[4];	//OBUID
	char transSerial[4];	//����˳��ţ����з���
	int consumeMoney;	//�ۿ���
};

//���ڽ��׽��
struct ExitTradeResult{
	char obuid[4];	//OBUID
	char tradeResult;	//����״̬	0-���׳ɹ�����0-����ʧ��
	long wrFileTime;	//д�ļ�ʱ��
	char psamNo[6];	//PSAM���ն˻����
	char transTime[7];	//����ʱ�䣬��ʽYYYYMMDDHHMMSS
	char transType;	//��������
	char tac[4];	//TAC
	char iccPaySerial[2];	//CPU���������
	char psamTransSerial[4];	//PSAM���������
	int cardBalance;	//���׺��������ȡ���ʧ�ܣ����ظ���
	StationRegisterInfo stationRegisterInfo;
	StaffInfo staffInfo;
};

//��վ��Ϣ-ֻȡ���õ�
struct StationPassInfo{
	char roadNetId[2];	//·�����
	char stationId[2];	//�շ�վ���
	char laneId;	//������
	long passTime;	//ͨ��ʱ��-UNIXʱ��
	char vehicleType;	//����
	char state;	//�����״̬��01-MTC��ڣ�02-MTC����
	char tollCollectorId[3];	//�շ�Ա����
	char classOrder;	//���
	char vehicleLicencePlateNumber[12];	//���ƺ�
};

//IC��Ƭ������Ϣ-ֻȡ���õ�
struct ICCIssuerInfo{
	char cardType;	//��Ƭ���ͣ�22-��ֵ����23-���˿�
	char cardNetId[2];	//��Ƭ������
	char cpuCardInnerId[8];	//CPU���ڲ����
};

//IC��������Ϣ
struct ICCTradeInfo{
	char etcPsamId[6];
	char etcPsamTradeNum[4];
	char tacCode[4];
	long dueToll;	//Ӧ�ۿ�
	long balanceBeforeTrade;	//����ǰ���
	long balanceAfterTrade;	//���׺����
	StationPassInfo entryStationInfo;
	StationPassInfo exitStationInfo;
	ICCIssuerInfo iccInfo;
};