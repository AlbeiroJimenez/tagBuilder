import tkinter as tk
from tagGUI.tagGUI import FrameWork2D, tagFrontEnd
# from tagModules.urlExtractor import urlDomains
# from tagModules.pixelBot import pixelBot
# from tagModules.handleFile import xlsxFile

if __name__ == '__main__':
    # webSite = urlDomains('https://www.xaxis.com/')
    # bot = pixelBot()
    # excel = xlsxFile()
    root = tk.Tk()
    tagCalc = tagFrontEnd(root)
    #tagCalc = tagFrontEnd(root, webSite, excel, bot)
    tagCalc.mainloop()