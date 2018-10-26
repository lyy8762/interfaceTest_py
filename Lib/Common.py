# -*- coding: utf-8 -*-
import time
import os
import win32com.client
import httplib
from IniParser import IniParser



def isNumeric(s):
    '''returns True if string s is numeric'''
    return all(c in "0123456789.+-" for c in s) 

def initEnv(src,dst):
    '''清理环境'''
    os.system('taskkill /f /im excel.exe')
    copyReportXls(src,dst)
    
def replaceData(data):
    '''excel中含有中文字符进行转换'''
    data = str(data).strip().replace("\n","").replace("”","\"").replace("‘","\'").replace("’","\'").replace("；",";")
    if data.endswith(";"):
        data = data[:-1]
    return data.split(";")

        
def convertToDict(obj):
    '''把Object对象转换成Dict对象'''
    dict = {}
    dict.update(obj.__dict__)
    return dict

# def PrintErrInfo():
#     # 获取异常函数及行号
#     try:
#         raise Exception
#     except:
#         f = sys.exc_info()[2].tb_frame.f_back
#     print (f.f_code.co_name, f.f_lineno)  


  

def retrieveDataSheetContent(pathName,sheetName,text, columnid, getColStart, columnCount, dataObj,qRun):
    ''' 读取xls中的值以字典的形式传出'''
#     print "return:",sheetName,text
    conn = win32com.client.Dispatch('ADODB.Connection')
    strConn = "Provider=Microsoft.ACE.OLEDB.12.0; Data Source = " + pathName +";Extended Properties='Excel 12.0 Xml;HDR=YES;IMEX=1'"
    conn.Open(strConn)
    eRes = win32com.client.Dispatch('ADODB.Recordset')
    sql="select * from ["+sheetName+"$] "
    eRes.Open(sql,conn, 1, 3)
    dataObj={}
    while not eRes.EOF:
        
        if qRun != '':
            if eRes.Fields(columnid-1).Value==text and eRes.Fields(1).Value==qRun:
                for j in range(0,columnCount-getColStart+1):
                    if type(eRes.Fields(j+getColStart-1).Value) !=None:
                        dataObj[j]=eRes.Fields(j+getColStart-1).Value
                    else:
                        dataObj[j]=""
                    
        else:
            if eRes.Fields(columnid-1).Value==text:
                for j in range(0,columnCount-getColStart+1):
                    if type(eRes.Fields(j+getColStart-1).Value) !=None:
                        dataObj[j]=eRes.Fields(j+getColStart-1).Value
                    else:
                        dataObj[j]=""
        eRes.MoveNext()
    eRes.Close()
    del eRes
    del conn
    return dataObj



 
#执行http接口调用
def HttpInvoke(IPPort, url):
    conn = httplib.HTTPConnection(IPPort)
    try:
        conn.request("GET", url)
    except:                                             
        try:
            conn.close()
            del conn
            time.sleep(30)
            conn = httplib.HTTPConnection(IPPort)
            conn.request("GET", url)
        except:
            print "Connect Failed"
    rsps = conn.getresponse()
    data = rsps.read().replace("&", "&amp;") 
    rsps.close()
    conn.close()
    del rsps
    del conn
    return data



def getTime():
    '''获取当前时间，格式为%Y%m%d %H:%M:%S'''
    import time
    return time.strftime('%Y%m%d %H:%M:%S',time.localtime(time.time()))



def rowCount(filePath,sheetName):
    '''获取xls的行数'''
    etObj = win32com.client.Dispatch("excel.Application")   #MS:Excel  WPS:et
    etFile = etObj.Workbooks.Open(filePath)
    etSheet = etFile.worksheets(sheetName)
    tmp=etSheet.UsedRange.Rows.Count
#     etFile.close()
    del etObj
    del etFile
    del etSheet
    return tmp
 
def columCount(filePath,sheetName):
    '''获取xls的列数'''
    etObj = win32com.client.Dispatch("excel.Application")   #MS:Excel  WPS:et
    etFile = etObj.Workbooks.Open(filePath)
    etSheet = etFile.worksheets(sheetName)
    tmp=etSheet.UsedRange.Columns.Count
#     etFile.close()
    del etObj
    del etFile
    del etSheet
    return tmp



def copyReportXls(src,dst):
    '''拷贝Report模板文件'''    
    import shutil
    if not os.path.exists(src):
        print "找不到报告模板文件"
        exit()
    
    shutil.copyfile(src, dst)


def getCalTime():
    '''获取当前时间'''
    import datetime
    return datetime.datetime.now()

    
def codeChange(vstring):
    '''code 转换'''
    if type(vstring)==type(u"unicode"):
        return vstring.encode("utf8")
    else:
        return str(vstring)
        



