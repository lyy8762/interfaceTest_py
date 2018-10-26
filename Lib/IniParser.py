# -*- coding: utf-8 -*-

import os
import ConfigParser

class IniParser:
    '''ini文件操作'''
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open("%s/Data/Configuration.ini" %os.getcwd()[:-4]))
        
    def getIniInfo(self,section, option):
        return self.config.get(section,option)
    
    def setIniInfo(self,section,option, val):
        return self.config.set(section,option,val)
    
