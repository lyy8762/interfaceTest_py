# -*- coding: utf-8 -*-
import copy
from ThriftSys import *
from OperateExcelDB import OperateExcelDB
from Excel import Excel


def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    
    workflowObj={}
    datasheetObj={}
    totalSucCount=0
    totalFailedCount=0
    detail = ""
    report_row=2
    projectDir=os.getcwd()[:-4]
    iniParser=IniParser()
    
    frameWorkPath="%s/Data/Framework.xls" %projectDir
    reportPath="%s%s" %(projectDir,iniParser.getIniInfo("sys","reportPath"))
    reportSrc="%s%s" %(projectDir,iniParser.getIniInfo("sys","reportModelPath"))
    reportDst="%s%s" %(projectDir,iniParser.getIniInfo("sys","reportPath"))
    strbktDefaultDic=iniParser.getIniInfo("trade", "TRADE_DEFAULT_DIC")
    socketIp=iniParser.getIniInfo("sys", "SocketIp")
    intSocket=iniParser.getIniInfo("sys", "IntSocket")
    version=iniParser.getIniInfo("sys", "Version")
    caseListSheet=iniParser.getIniInfo("sys", "CaseListSheet")
    dataPath=iniParser.getIniInfo("sys", "DataPath")
    
    initEnv(reportSrc,reportDst)
    reportObj=Excel(reportPath)
    
    
    sqlFramework="select * from [%s$]" %caseListSheet
    bktDefaultDic=json.loads(strbktDefaultDic)
    backDic=copy.deepcopy(bktDefaultDic)
    excelDb=OperateExcelDB(frameWorkPath)           
    frameworkRes=excelDb.Open(sqlFramework)
    while not frameworkRes.EOF:
        caseSucCount=0
        caseFailedCount=0
        if frameworkRes.Fields(2).value == 'Y':
            log.Output(frameworkRes.Fields(1).Value)
            log.Output("-------------------------------------------------")
            workflowSheet = frameworkRes.Fields(3).Value
            workFlowName = frameworkRes.Fields(4).Value
#             dataPath = frameworkRes.Fields(5).Value
            rCount = rowCount("%s\data\%s" %(projectDir,workFlowName),workflowSheet)
            colCount = columCount("%s\data\%s" %(projectDir,workFlowName),workflowSheet)
            workflowObj = retrieveDataSheetContent("%s\data\%s" %(projectDir,workFlowName),workflowSheet, "Workflow",4,5,colCount,workflowObj,"Y")
            datasheetObj = retrieveDataSheetContent("%s\data\%s" %(projectDir,workFlowName),workflowSheet,"DataSheet",4,5,colCount,datasheetObj,"Y")
            casedataObj = {}
            for j in xrange(rCount-3):
                dataidObj = {}
                dataidObj = retrieveDataSheetContent("%s\data\%s" %(projectDir,workFlowName),workflowSheet,str(j+1),1,5,colCount,dataidObj,"Y")
                descriptObj = retrieveDataSheetContent("%s\data\%s" %(projectDir,workFlowName),workflowSheet,str(j+1),1,3,3,dataidObj,"Y")
                if dataidObj=={}:
                    continue
                log.Output("  case:%s %s" %(j+1,descriptObj[0]))
                log.Output("  --------------------------------------------")
                sessionId =""
                fundid = "" 
                orderNo =sno=""
                for i in xrange(0,len(workflowObj)):
                    try:
                        if dataidObj[i]!=None:
                            iFlag = False
                            log.Output("%s%s:%s" %("    ",workflowObj[i],dataidObj[i]))
                            log.Output("     --------------------------------------------")
                            strData = ("%s\data\%s" %(projectDir,"%s" %dataPath)).decode('utf-8')
#                             strData = ("%s\Data\%s\%s.xls" %(projectDir,dataPath,datasheetObj[i])).decode('utf-8')
                            caseColCount = columCount(strData,datasheetObj[i])
#                             caseColCount = columCount(strData,datasheetObj[i])
                            casedataObj = retrieveDataSheetContent(strData,datasheetObj[i],dataidObj[i],1,2,caseColCount,casedataObj,"")
                            if casedataObj == {}:
                                log.Output("     [InterfaceResult]:Failed,casedata数据返回为空，请检查数据的正确性","error")
                                continue
                            
                        
                            if workflowObj[i]=="customerService.getVerificationCode":
                                adic =bktDefaultDic[workflowObj[i]]
                                iFlag,getVerificationCode=thriftInterface(socketIp,intSocket,version,dataidObj[i],casedataObj[0],casedataObj[1],casedataObj[2],adic,workflowObj[i],reportObj,report_row)
                                continue
                            elif workflowObj[i]=="customerService.login":
                                verifyCode=getVerificationCode["data"]["verifyCode"]
                                adic =bktDefaultDic[workflowObj[i]]
                                adic["CommonRequest"]["dynamicMap"]["verifyCode"]=verifyCode
                                iFlag,login=thriftInterface(socketIp,intSocket,version,dataidObj[i],casedataObj[0],casedataObj[1],casedataObj[2],adic,workflowObj[i],reportObj,report_row)
                                if login['data'] != {}:
                                    sessionId=login["sessionId"]
                                    fundid=login["data"][0]["fundid"]
                                continue
                    
                            if workflowObj[i] in []:
                                adic =bktDefaultDic[workflowObj[i]]
                                iFlag,getVerificationCode=thriftInterface(socketIp,intSocket,version,dataidObj[i],casedataObj[0],casedataObj[1],casedataObj[2],adic,workflowObj[i],reportObj,report_row)
                                continue
                                    
                            elif workflowObj[i] in ["customerService.isShowAgreement","mobileTransService.verfyLogin","mobileTransService.getSecurities"]:
                                # need none
                                adic = commonBKTDic(bktDefaultDic,workflowObj[i])
                                iFlag,noreCommon=thriftInterface(socketIp,intSocket,version,dataidObj[i],casedataObj[0],casedataObj[1],casedataObj[2],adic,workflowObj[i],reportObj,report_row)
                                continue
                            #need get sessionid from login interface
                            elif workflowObj[i] in ["bankStockService.queryBankTrans","tradeService.confirmTrans","queryService.queryStock","queryService.queryDone","queryService.queryOrders","queryService.getMaxTranseCount","queryService.queryAvailableFund","tradeService.cancelTrans","tradeService.changeTrans","bankStockService.transferBankToSecurity","bankStockService.transferSecurityToBank","bankStockService.queryBankSecuTrans","customerService.queryUserInfo","customerService.modifyUserInfo","customerService.forgotPassword","tradeService.confirmCombination","bankStockService.queryBalance","bankStockService.transferAccount","bankStockService.queryBankList"]:
                                adic = commonBKTDic(bktDefaultDic,workflowObj[i],sessionId,fundid)
                                if workflowObj[i]=="tradeService.cancelTrans":
                                    adic["CommonRequest"]["dynamicMap"]["ordersno"]=orderNo
#                                 elif workflowObj[i]=="bankStockService.queryBankSecuTrans":
#                                     adic["CommonRequest"]["dynamicMap"]["sno"]=sno
                                elif workflowObj[i]=="tradeService.changeTrans":
                                    adic["CommonRequest"]["dynamicMap"]["ordersno"]=orderNo
                                else:
                                    pass
#                                 time.sleep(5)
                                iFlag,noreCommon=thriftInterface(socketIp,intSocket,version,dataidObj[i],casedataObj[0],casedataObj[1],casedataObj[2],adic,workflowObj[i],reportObj,report_row)
#                                 if workflowObj[i]=="tradeService.confirmTrans":
#                                     if noreCommon['data'] != {}:
#                                         orderNo=noreCommon["data"]["ordersno"]
                                if workflowObj[i]=="bankStockService.transferAccount":
                                    if noreCommon['data'] != {}:
                                        sno=noreCommon["data"]["sno"]
                                        #get ordersno from queryOrders
                                elif  workflowObj[i]=="queryService.queryOrders":
                                    if noreCommon['data'] != []:
                                        orderNo=noreCommon["data"][0]["ordersno"]
                                else:
                                    pass
                                continue
                                
                            elif workflowObj[i] in ["customerService.logout","queryService.queryMatch","queryService.queryFund","queryService.queryMarket","queryService.queryMatchExact","queryService.queryStockCombination","bankStockService.thirdManagement"]:
                                #need get sessionID
                                adic = commonBKTDic(bktDefaultDic,workflowObj[i],sessionId)
                                iFlag,noCommon=thriftInterface(socketIp,intSocket,version,dataidObj[i],casedataObj[0],casedataObj[1],casedataObj[2],adic,workflowObj[i],reportObj,report_row)
                                continue
                            elif workflowObj[i] in ["securityDetailThriftService.queryStock","securityDetailThriftService.queryFund","securityDetailThriftService.queryBond","securityDetailThriftService.queryCBond","rrThriftService.queryRrList","rrThriftService.queryRrInfo","lcThriftService.queryAcList","lcThriftService.queryAcInfo","securityDetailThriftService.queryShareInfo","securityDetailThriftService.querySecurity","securityDetailThriftService.querySecurityBrief","securityQuotationThriftService.queryHistory"
                                                    ,"tradingDayThriftService.isTradingDay","tradingDayThriftService.queryPrevTradingDay","tradingDayThriftService.queryFiveDays","hkSecurityThriftService.queryInfo","hkSecurityThriftService.queryRight","hkSecurityThriftService.queryQuote","hkSecurityThriftService.queryEx"]:
                                #need get sessionID
                                adic = {}
                                iFlag,noCommon=thriftInterface(socketIp,intSocket,version,dataidObj[i],casedataObj[0],casedataObj[1],casedataObj[2],adic,workflowObj[i],reportObj,report_row)
                                continue
                            elif workflowObj[i] in ["api.thrift.quotation.security.query","api.thrift.quotation.realtime","api.thrift.quotation.simple","api.thrift.quotation.timeTrend.query","api.thrift.quotation.timeTrend.queryFive","api.thrift.quotation.kline.query","api.thrift.quotation.security.queryAll"]:
                                # need none
                                adic = {}
                                iFlag,noreCommon=thriftInterface(socketIp,intSocket,version,dataidObj[i],casedataObj[0],casedataObj[1],casedataObj[2],adic,workflowObj[i],reportObj,report_row)
                                
                    except Exception,e:
                            log.Output("     exception:%s" %e,"error")
                            iFlag = False
                    finally:        
                        bktDefaultDic=copy.deepcopy(backDic)
                        report_row+=1
                        if not iFlag:
                            break
                            
                if iFlag:
                    log.Output("  [CaseResult]:Pass")
                    caseSucCount+=1
                    totalSucCount+=1
                else:
                    log.Output("  [CaseResult]:Failed","error")
                    caseFailedCount+=1
                    totalFailedCount+=1
        
        if caseSucCount+caseFailedCount !=0:
            detail = "%s%s 共运行%s个TestCase,成功%s个,失败%s个   \n" %(detail,frameworkRes.Fields(1).Value,caseSucCount+caseFailedCount,caseSucCount,caseFailedCount)          
        frameworkRes.MoveNext()
        
    del frameworkRes
    log.Output("*************************************************************************************************************************")
    log.Output("*****TestCase Total:%s,Succ:%s,Failed:%s" %(totalSucCount+totalFailedCount,totalSucCount,totalFailedCount))
    log.Output(detail)
    

        
if __name__=="__main__":
    main()

    

    





