# -*- coding: utf-8 -*-
import win32com.client
OK_COLOR = 0xffffff
NG_COLOR = 0xff
NT_COLOR = 0xC0C0C0

class Excel:
#excel的各种操作

    def __init__(self, sFile):
        self.xlApp = win32com.client.Dispatch("Excel.Application")   #MS:Excel  WPS:et
        try:
            self.book = self.xlApp.Workbooks.Open(sFile)
        except Exception,e:
#             PrintErrInfo()
            print e
            print "打开文件失败"
            exit()

    def close(self):
        #self.book.Close(SaveChanges=0)
        self.book.Save()
        self.book.Close()
        self.xlApp.Quit()
        del self.xlApp
        del self.book
        print ""
        
    def readData(self, iSheet, iRow, iCol):
        try:
            sht = self.book.Worksheets(iSheet)
            sValue = str(sht.Cells(iRow, iCol).Value)
        except:
            self.close()
            print "读取数据失败"
            exit()
        #去除'.0'
        if sValue[-2:] == '.0':
            sValue = sValue[0:-2]
        return sValue

    def writeData(self, iSheet, iRow, iCol, sData, color=OK_COLOR):
        try:
            sht = self.book.Worksheets(iSheet)
            sht.Cells(iRow, iCol).Value = str(sData).decode("utf-8")
            sht.Cells(iRow, iCol).Interior.Color = color
            self.book.Save()
        except:
            self.close()
            print "写入数据失败"
            exit()
            
    #获取用例个数    
    def getNcase(self, iSheet):
        try:
            return self.get_nrows(iSheet) - self.casebegin + 1
        except:
            self.close()
            print "获取Case个数失败"
            exit()
    
    def getNrows(self, iSheet):
        try:
            sht = self.book.Worksheets(iSheet)
            return sht.UsedRange.Rows.Count
        except:
            self.close()
            print "获取nrows失败"
            exit()

    def getNcols(self, iSheet):
        try:
            sht = self.book.Worksheets(iSheet)
            return sht.UsedRange.Columns.Count
        except:
            self.close()
            print "获取ncols失败"
            exit()


def writeReportSum(path,caseSucCount, caseLosCount,caseNRCount,interfaceSucCount,interfaceLosCount,interfaceNRCount,checkPointSucCount, checkPointLosCount, startTime): 
    oExcel=Excel(path)
    
    oExcel.write_data(1, 19, 2,caseSucCount)
    oExcel.write_data(1, 20, 2,caseLosCount)
    oExcel.write_data(1, 22, 2,caseNRCount)
    
    oExcel.write_data(1, 19, 4,interfaceSucCount)
    oExcel.write_data(1, 20, 4,interfaceLosCount)
    oExcel.write_data(1, 22, 4,interfaceNRCount)
    
    oExcel.write_data(1, 19, 6,checkPointSucCount)
    oExcel.write_data(1, 20, 6,checkPointLosCount)
    
    oExcel.close()
    del oExcel