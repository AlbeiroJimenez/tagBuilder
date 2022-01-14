import tkinter as tk
from tagGUI.tagGUI import FrameWork2D, tagFrontEnd
from tagModules.urlExtractor import urlDomains
from tagModules.handleFile import xlsxFile

if __name__ == '__main__':
    webSite = urlDomains('https://www.xaxis.com/')
    excel = xlsxFile()
    root = tk.Tk()
    tagCalc = tagFrontEnd(root, webSite, excel)
    tagCalc.mainloop()