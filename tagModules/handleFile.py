from openpyxl import Workbook,load_workbook
from openpyxl.styles import Alignment
from datetime import date as dt

from os import path as p

MONTHS  = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]

TRIGGER = [
    'PV', 'Click', 'Scroll'
    ]

SHEET_NAME = 'Tagging Request'

class xlsxFile:
    def __init__(self, sheet = 'Tagging Request',PATH='TaggingRequest_2021.xlsx'):
        self.PATH = p.abspath(PATH)
        self.setBook()
        self.sheet = self.book[sheet]
        
    def setPATH(self, path):
        self.PATH = p.abspath(path)
    
    def setBook(self):
        self.book = load_workbook(self.PATH)
        
    def saveBook(self, dir_path = None):
        nameFile = self.getFileName('C13')
        if dir_path == None:
            self.book.save(nameFile)
        else:
            self.book.save(p.join(dir_path, nameFile))
        #self.book.save(self.PATH)
        
    def setSheet(self, nameSheet = SHEET_NAME):
        self.sheet = self.book[nameSheet]
        
    def duplicateSheet(self, nameSheetFrom, nameSheetTo):
        self.setSheet(nameSheetFrom)
        self.book.copy_worksheet(self.sheet).title = nameSheetTo
        
    def setSectionSheets(self, nameSheetFrom, sectionList):
        for section in sectionList:
            self.duplicateSheet(nameSheetFrom, section)
    
    def loadList(self, dataList, cellOrigin = 'F31'):
        cell = cellOrigin
        for item in dataList:
            cell = self.getCellDown(cell)
            self.sheet[cell] = item

    def readCell(self, cell):
        return self.sheet[cell].value
    
    def writeCell(self, cell, value, aligment_=['center','center']):
        self.sheet[cell] = value
        cell = self.sheet[cell]
        cell.alignment = Alignment(horizontal=aligment_[0], vertical=aligment_[1])

    def getCellDown(self, cell):
        for i in range(0,len(cell)):
            if cell[i].isdigit():
                return cell[0:i]+str(int(cell[i:])+1)
            
    def getCellUp(self, cell):
        for i in range(0,len(cell)):
            if cell[i].isdigit():
                return cell[0:i]+str(int(cell[i:])-1)
            
    def getLastPath(self, path):
        return path[1:].split('/')[0]
            
    def getDate(self):
        month = ''
        for i in range(1,13):
            if dt.today().month == i:
                month = MONTHS[i-1]
        return month, str(dt.today().year)
            
    def getFileName(self, cell):
        advertiser  = self.readCell(cell)
        month, year = self.getDate()
        return 'TagReq_'+advertiser+'_'+month+year+'.xlsx'

    def getNameSection(self, advertiserName, sectionName, typeTrigger='PV'):
        month, year = self.getDate()
        return advertiserName+'_'+sectionName+typeTrigger+'_'+month+year
    
    def getTagName(self, path, cell):
        advertiser  = self.readCell(cell) 
        month, year = self.getDate()
        lastPath    = self.getLastPath(path)
        trigger     = 'PV'
        if lastPath == '':
            lastPath = 'Home'
        return advertiser+'_'+lastPath.capitalize()+trigger+'_'+month+year+'.xlsx'
        
            
if __name__ == '__main__':
    file = xlsxFile()