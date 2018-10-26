# -*- coding: utf-8 -*-
import win32com.client
class OperateExcelDB:
    '''以DB的方式打开xls'''
    def __init__(self, excelPath):
        self.conn = win32com.client.Dispatch('ADODB.Connection')
        strConn = "Provider=Microsoft.ACE.OLEDB.12.0; Data Source = " + excelPath +";Extended Properties='Excel 12.0 Xml;HDR=YES;IMEX=1'"
        try:
            self.conn.Open(strConn)
        except Exception,e:
            print e
        self.eRes = win32com.client.Dispatch('ADODB.Recordset')
    
    def Open(self, sql):
        self.eRes.Open(sql,self.conn, 1, 3)
        return self.eRes
        
    def CloseOp(self):
        self.eRes.Close()
        del self.eRes
        del self.conn





