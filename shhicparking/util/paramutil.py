#encoding:utf-8
'''
Created on 2015-6-19
全局参数工具
@author: user
'''
import json
import os
import shutil
import codecs

from threading import RLock

class ParamHolder:
    def __init__(self,dumpFile = None,encryFun = lambda x:x,decryFun = lambda x:x):
        self.dumpFile = dumpFile
        self.param = {}
        self.lock = RLock()
        self.encryFun = encryFun
        self.decryFun = decryFun    #加解密函数
        if dumpFile is not None:
            self.__loadParameterFromLocalFile()
        
    def loadParameterFromLocalFile(self,configFile):
        self.dumpFile = configFile
        self.__loadParameterFromLocalFile()
    
    def __loadParameterFromLocalFile(self,withTmpFile = False):
        '''从本地配置文件中获取配置'''
        f = None
        try:
            f = codecs.open(self.dumpFile,'r','utf-8')
            fs = f.read()
            self.param = json.loads(self.decryFun(fs),encoding="utf-8")
        except Exception,e:
            print "load parameter from local file error:",e
        finally:
            if f is not None:f.close()
    
    def dumpParameterToLocalFile(self):
        '''配置保存到本地文件'''
        f = None
        try:
            self.lock.acquire()
            toSaveStr = self.encryFun(json.dumps(self.param,encoding="utf-8",indent=1,ensure_ascii=False))
            print toSaveStr
            f = codecs.open(self.dumpFile,'w','utf-8')
            f.write(toSaveStr)
        finally:
            if f is not None:f.close()
            self.lock.release()
                
    def clearAll(self):
        self.param.clear()
    
    def __getitem__(self,key):
        if key not in self.param:
            raise Exception("需要的属性[%s]不在这里面"%key)
        return self.param[key]
    
    def __setitem__(self,key,value):
        self.lock.acquire()
        self.param[key] = value
        self.lock.release()

    def __contains__(self,key):
        return key in self.param
    
    def __delitem__(self,key):
        self.lock.acquire()
        if key in self.param:
            del self.param[key]
        self.lock.release()
        
    def __len__(self):
        return len(self.param)

    def isEmpty(self):
        return len(self.param) == 0