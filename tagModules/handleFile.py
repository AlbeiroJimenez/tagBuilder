from openpyxl import Workbook,load_workbook
from openpyxl.styles import Alignment
from datetime import date as dt

from os import path as p
import re

MONTHS  = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]

TRIGGER = [
    'PV', 'Click', 'Scroll'
    ]

SHEET_NAME = 'Tagging Request'

PATH_      = 'TaggingRequest_2021.xlsx'

class xlsxFile:
    def __init__(self, sheet = 'Tagging Request', PATH=PATH_):
        self.PATH = PATH
        self.setBook()
        self.sheet = self.book[sheet]
        
    def setPATH(self, path=PATH_):
        self.PATH = path
    
    def setBook(self):
        self.book = load_workbook(p.abspath(self.PATH))
        
    def saveBook(self, dir_path = None, default_name=True):
        if default_name:
            nameFile = self.getFileName('C13')
        else:
            nameFile = self.getFileName('C13', 'Final')
        if dir_path == None:
            self.book.save(nameFile)
            return p.abspath(nameFile).replace('\\','/')
        else:
            self.book.save(p.join(dir_path, nameFile))
            return dir_path+'/'+nameFile
        
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
    
    def readNextCell(self, cell, direction='vertical'):
        """Function to get the value store in the neighborhood cells.

        Args:
            cell (str): Name cell with excel nomenclature. e.g E32
            direction (str, optional): Direction of the search of our cell neighborhood. Defaults to 'vertical'.

        Returns:
            Value Cell: The value stores in the neighborhood cell.
        """
        cell = cell.upper()
        if direction == 'vertical':
            nextCell = re.findall(r'\D+', cell)[0]+str(int(re.findall(r'\d+', cell)[0])+1)
            return nextCell, self.readCell(nextCell)
        else:
            row, col = int(re.findall(r'\d+', cell)[0]), self.getColIndex(re.findall(r'\D+', cell)[0])+1
            return self.sheet.cell(row, col).coordinate, self.sheet.cell(row, col).value
            
    def getColIndex(self, colString):
        """Function to mappear from name column domain to numeric column index.

        Args:
            colString (str): Name of the column in excel format: AAK, A, etc

        Returns:
            colIndex: column index.
        """
        colIndex = 0
        for c,e in zip(colString, range(len(colString)-1,-1,-1)):
            colIndex = colIndex + (ord(c)-64)*pow(26, e)
        return colIndex
    
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
            
    def getFileName(self, cell, custom_text=''):
        advertiser  = self.readCell(cell)
        month, year = self.getDate()
        return 'TagReq'+custom_text+'_'+advertiser+'_'+month+year+'.xlsx'

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
