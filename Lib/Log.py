# -*- coding: utf-8 -*-
import os
class PrintLogInfo:
    '''日志打印'''
    def __init__(self):
    #初始化
        try:
            import logging, time
            self.logger = None
            self.logger = logging.getLogger()
            logname= time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
            projectDir=os.getcwd()[:-4]
            logfile=projectDir+"/Log/"+logname+".log"
            self.hdlr = logging.FileHandler(logfile)
            formatter = logging.Formatter("[%(asctime)s %(levelname)s]: %(message)s","%Y-%m-%d %H:%M:%S")
            self.hdlr.setFormatter(formatter)
            self.logger.addHandler(self.hdlr)
            self.logger.setLevel(logging.DEBUG)
        except:
            print "log init error!"

    def Output(self,logInfo, logclass="info"):
    #打印
        if len(logInfo)>1000:
            logInfo = logInfo[:10000]
        
#         logInfo=str(logInfo).decode("utf-8")
        print logInfo
        try:
            if  logclass=="info":
                self.logger.info(logInfo)
            elif logclass=="error":
                self.logger.error(logInfo)
            elif logclass=="debug":
                self.logger.debug(logInfo)
            elif logclass=="warning":
                self.logger.warning(logInfo)
            
        except:
            print "log output error!"

    def close(self):
    #关闭
        try:
            self.logger.removeHandler(self.hdlr)
        except Exception,e:
            print "log closed error!"
            





