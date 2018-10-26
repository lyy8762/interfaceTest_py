# -*- coding: utf-8 -*-

import json
import sys
from thrift.protocol.TMultiplexedProtocol import TMultiplexedProtocol
sys.path.append('../ThriftServer')

from cn.jsfund.thrift.mvc import Bkt
from cn.jsfund.thrift.mvc.ttypes import *
from thrift.transport import TSocket
from thrift.transport import TSSLSocket
from thrift.transport import TTransport
from thrift.protocol import TCompactProtocol
from Log import PrintLogInfo
from Common import *
import time


log = PrintLogInfo()

def thriftInterface(socketIp,intSocket,version,dataid,exceldata,outcheck,outresult,adic,api,reportObj,report_row):
    interfaceResult=True
    
    inputResult=inputDataOprate(exceldata,adic)
    if not inputResult:
        return False
    transport = TSocket.TSocket(socketIp,intSocket)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TCompactProtocol.TCompactProtocol(transport)
    p = TMultiplexedProtocol(protocol, "bkt")
    
    client = Bkt.Client(p)
    
    transport.open()
    
    request=Request()
    request.api=api
    request.version=version
    request.data=json.dumps(adic,ensure_ascii=False)
    try:
        output=client.api(request)
    except Exception,e:
        reportObj.writeData(2,report_row, 1, adic)
        reportObj.writeData( 2,report_row, 2, str(e._message).encode("utf-8"))
        if outcheck!=None:
            message=str(outcheck).replace("：", ":").split(":=")[1]
            if message==e._message.encode("utf-8"):
                return True,"pass"
            log.Output("        [Failed]:%s expect is %s,real is %s" %("message",message,str(e._message).encode("utf-8")),'error')

        log.Output("        input:%s" %adic)
        log.Output("        thrift异常:%s" %str(e._message).encode("utf-8"))
        transport.close()
        return False,e
    
    output=convertToDict(output)
    coutput=json.dumps(output["data"],ensure_ascii=False)
    output=json.dumps(output,ensure_ascii=False)
    checData=json.loads(coutput.replace("\n", " ").replace(":null", ":None").replace("false", "'false'").replace("true", "'true'")).encode('utf-8')
    checData=eval(checData)
    if outcheck!="" and outcheck!=None:
        dataCheck=checkDataOprate(outcheck,checData)                 #output.data检查
        if not dataCheck:
            interfaceResult = False
            
    if outresult!="" and outresult!=None:
        resultCheck=checkDataOprate(outresult,eval(output))             #output检查
        if not resultCheck:
            interfaceResult = False 
            
    if "api.thrift.quotation" in api:
        dataItemFlag=quotationItemCheck(checData,api,adic)
        quotationOtherFlag=quotationOtherCheck(checData,api,adic)
        if not quotationOtherFlag:
            interfaceResult = False
    elif "data"  in checData: 
        dataItemFlag=dataItemCheck(checData['data'])                     #output.data.data子项不为空检查
    else:
        dataItemFlag=dataItemCheck(checData) 
    
    if not dataItemFlag:
        interfaceResult = False
        
    transport.close()
    if interfaceResult:
#         log.Output("     [InterfaceResult]:Pass")
#        log.Output("        input:%s" %adic)
#        log.Output("        output:%s" %output)
        pass
    else:
        log.Output("     [InterfaceResult]:Failed","error")
        log.Output("        input:%s" %adic)
        log.Output("        output:%s" %output)
        
    reportObj.writeData(2,report_row, 1, adic)
    reportObj.writeData(2,report_row, 2, output)
    return interfaceResult,checData

def inputDataOprate(exceldata,sdic):
    
    usedata=replaceData(exceldata)
    if usedata in [[''],['None']]:
        return True
    for i in usedata:
        if ":=" not in i:
            log.Output("        输入的数据有误： %s" %i,'error')
            return False
        try:
            sname=str(i).split(":=")[0].strip()
            svalue=str(i).split(":=")[1].strip()
            obj=""
            if svalue.startswith("["):
                try:
                    svalue = eval(svalue)
                except Exception,e:
                    log.Output(e,"error")
            for i in sname.split("."):
                if isNumeric(i):
                    obj="%s[%s]" %(obj,i)
                else:
                    obj="%s['%s']" %(obj,i)
            scmd ='''%s%s=%s''' %("sdic",obj,svalue)
            exec(scmd)
            
        except Exception,e:
            log.Output("输入的数据有误：%s" %usedata,"error")
            return False
    return True
        
def checkDataOprate(exceldata,sdic):
    usedata=replaceData(exceldata)
    flag ="True"
    for i in usedata:
        if ":=" not in i:
            log.Output("        输入的数据有误： %s" %i,'error')
            return False
            
        sname=i.split(":=")[0].strip()
        svalue=str(i.split(":=")[1]).strip()
#     log.Output("sname is %s,svalue is " %sname,svalue)
        obj=scmd=realval=""
        for i in sname.split("."):
            if isNumeric(i):
                obj="%s[%s]" %(obj,i)
  #              log.Output("%s is the value of ifobj" %obj)
            else:
                obj="%s['%s']" %(obj,i)
  #              log.Output("%s is the value of elseobj" %obj)
  #      log.Output("the value of obj is %s" %obj)
        scmd = "%s%s" %("sdic",obj)
 #       log.Output("the value of scmd is %s" %scmd)
        try:
            realval=eval(scmd)
        except:
            log.Output("        [Failed]:命令转换出错,eval(%s)" %scmd,'error')
            flag = False
        
        if svalue =="不为空":
            if realval=={} or realval==[]:
                log.Output("        [Failed]:%s expect is %s,real is %s" %(sname,svalue,realval),'error')
                flag = False
            else:
                 log.Output("        [Pass]:%s expect is %s,real is %s" %(sname,svalue,realval))
                
            continue
        
        if svalue =="不为0":
            if realval=="0":
                log.Output("        [Failed]:%s expect is %s,real is %s" %(sname,svalue,realval),'error')
                flag = False
#             else:
#                 log.Output("        [Pass]:%s expect is %s,real is %s" %(sname,svalue,realval))
                
            continue
        if str(svalue)==str(realval):
            pass
#             log.Output("        [Pass]:%s expect is %s,real is %s" %(sname,svalue,realval))
        elif ".00" in str(realval):
            if str(svalue)==str(realval[:-3]):
                pass
            else:
                flag =False
                log.Output("        [Failed]:%s expect is %s,real is %s" %(sname,svalue,realval),'error')
        elif str(realval)=='0.0':
            if str(svalue) in ["0.0","0.00"]:
                pass
            else:
                flag =False
                log.Output("        [Failed]:%s expect is %s,real is %s" %(sname,svalue,realval),'error')
        elif str(svalue)=="null":
            if realval == None:
                pass
            else:
                flag =False
                log.Output("        [Failed]:%s expect is %s,real is %s" %(sname,svalue,realval),'error')
            
        else:
            if str(svalue)=="" and (realval ==[] or realval=={}):
                pass
            
                
                
#                 log.Output("        [Pass]:%s expect is %s,real is %s" %(sname,svalue,realval))
            else:
                log.Output("        [Failed]:%s expect is %s,real is %s" %(sname,svalue,realval),'error')
                flag = False
            
    return flag

def dataItemCheck(dataItems):
    #data子项不为空检查
    itemFlag = True
    if type(dataItems)==dict:
        for skey,sval in dataItems.items():
            if sval in ["",None,[],{}] :
                if skey not in["~creditflag1","stkcode","linkflag","vipid","identitysign","lastloginip","bankcode","lastloginmac","memotext","prodname","prodcode","custname","value","fundseq","fundpartavl","currency","precision","poststr","stkname","price","maxdownvalue","mtkcalflag","maxqty","minqty","bondintr","priceunit","moneytype","maxrisevalue","~cancelflag"]:
                    log.Output("        [Faild]:子项有空数据,key:%s,value:%s" %(skey,str(sval)), 'error')
                    itemFlag = False
            
                
    elif type(dataItems)==list:
        for dataItem in dataItems:
            if type(dataItem)==str:
                break
            for skey,sval in dataItem.items():
                if sval in ["",None,[],{}]:
                    if skey not in ["~creditflag1","stkcode","linkflag","vipid","identitysign","lastloginip","bankcode","lastloginmac","memotext","prodname","prodcode","custname","fundseq","fundpartavl","currency","precision","poststr","stkname","price","maxdownvalue","mtkcalflag","maxqty","minqty","bondintr","priceunit","moneytype","maxrisevalue","~cancelflag"]:
                        log.Output("        [Faild]:子项有空数据,key:%s,value:%s" %(skey,str(sval)), 'error')
                        itemFlag = False
    return itemFlag

def quotationItemCheck(checkdata,api,adic):
    import copy
    #data子项不为空检查
    itemFlag = True
    iniParser = IniParser()
    dic_keys=json.loads(iniParser.getIniInfo("quotation", "QUOTATION_ITEM"))
    try:
        akeys=dic_keys[api]
    except Exception,e:
        log.Output("        没有配置子项数据%s" %api, 'error')
    if "security.query" in api:
        if checkdata["securityList"]==[]:
            log.Output("        输入的数据有误",'error')
            return False
#     data_dic={"api.thrift.quotation.security.query":'checkdata["securityList"]',"api.thrift.quotation.realtime":'checkdata["quotationList"]',
#               "api.thrift.quotation.simple":'checkdata["simpleQuotationList"]',"api.thrift.quotation.timeTrend.query":'checkdata["quotationList"]',
#                 "api.thrift.quotation.security.queryAll":'checkdata["securityList"]'
#             }
    data_dic=json.loads(iniParser.getIniInfo("quotation", "QUOTATION_CHECK_LIST"))
    dataItems = eval("checkdata['%s']" %data_dic.get(api))
    for dataItem in dataItems:
        
        keys=copy.deepcopy(akeys)
        realkeys=dataItem.keys()
        for skey,sval in dataItem.items():
            if skey in keys:
                if sval in ["",None,[],{}] :
                    if skey not in["selllistIterator","buylistIterator","qty","shareList","secondIndustry","price"]:
                        log.Output("        [Faild]:子项有空数据,key:%s,value:%s" %(skey,str(sval)), 'error')
                        itemFlag = False
                keys.remove(skey)
                realkeys.remove(skey)
            
        if len(keys)!=0:
            itemFlag = False
            log.Output("        [Faild]:子项缺少必填项:%s" %keys, 'error')
                
        if len(realkeys)!=0:
            itemFlag = False
            log.Output("        [Faild]:存在多余子项:%s" %realkeys, 'error')
    return itemFlag

def quotationOtherCheck(checkdata,api,adic):
    Flag = True
    iniParser = IniParser()
    logFlag=iniParser.getIniInfo("quotation", "LOG_FLAG")
    if logFlag=="Y":
        log.Output("        %s" %checkdata)
    if "api.thrift.quotation.security.query"==api:
        pass
    elif "api.thrift.quotation.timeTrend.queryFive" == api:
        log.Output("        [获取时间]:%s" %getTime())
        for i in checkdata['timeTrends']:
            log.Output("        [五日分时图]:交易日%s,条数：%s" %(i['date'],len(i['list'])))
            if len(i['list'])!=242:
                log.Output("        [五日分时图]:交易日%s,条数：%s" %(i['date'],len(i['list'])),'error')
    elif "api.thrift.quotation.kline.query" == api:
        if int(adic['num'])!=len(checkdata['klineList']):
            Flag = False
            log.Output("        [Failed]:num expect is:%s,real is：%s" %(adic['num'],len(checkdata['klineList'])),'error')
    return Flag

def commonBKTDic(sdic,skey,*arg):
    adic =  sdic[skey]
    argLen = len(arg)
    if argLen==1:
        adic["CommonRequest"]["dynamicMap"]["sessionId"]=arg[0]
    if argLen==2:
        adic["CommonRequest"]["dynamicMap"]["sessionId"]=arg[0]
        adic["CommonRequest"]["dynamicMap"]["fundid"]=arg[1]
#     if argLen==3:
#         adic["CommonRequest"]["dynamicMap"]["sessionId"]=arg[0]
#         adic["CommonRequest"]["dynamicMap"]["fundid"]=arg[1]
#         adic["CommonRequest"]["dynamicMap"]["ordersno"]=arg[2]
    return adic
            
