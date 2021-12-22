import tkinter as tk
from tkinter import Button, filedialog, messagebox, ttk
from threading import Thread

from os import closerange, path as p
from urllib.parse import urlparse
from tkinter import font
from tkinter.constants import OFF

MENU_DEFINITION = (
            'File- &New/Ctrl+N/self.newFile, Save/Ctrl+S/self.save_file, SaveAs/Ctrl+Shift+S/self.save_as, sep, Exit/Ctrl+Q/self.exitCalcTag',
            'Edit- Setting/Ctrl+Z/self.setting, sep, Show Offline/Alt+F5/self.offline',
            'View- URL Extractor//self.show_urlExtractor, GTM//self.show_GTM',
            'Help- Documentation/F2/self.documentation, About/F1/self.aboutTagCalc'
        )

TABS_DEFINITION = (
    'SiteMap',
    'GTM'
    )

SPECIAL_CELLS   = (
    'C31', 'D31', 'G31'
)

PROGRAM_NAME = 'TagCalc'

class FrameWork2D(ttk.Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = root
        self.tabPages = ttk.Notebook(self.root)
        self.build_menu(MENU_DEFINITION)
        self.build_tabs(TABS_DEFINITION)
        self.GTM = True
        self.set_CCS()
        
    def set_CCS(self):
        self.root.title(PROGRAM_NAME)
        self.root.iconbitmap('xaxis32x32.ico')
        #self.root.iconify()
        #self.root.attributes("-alpha", 0.5)
        #785x400+300+100
        self.root.geometry("795x415+300+100")
        self.root.resizable(False,False)
        self.root.configure(bg='white')
        style = ttk.Style()
        if 'xpnative' in style.theme_names():
            style.theme_use('xpnative')
        elif 'vista' in style.theme_names():
            style.theme_use('vista')
        elif 'clam' in style.theme_names():
            style.theme_use('clam')
        else:
            style.theme_use('default')
        style.configure('.', padding=3, font=('Arial',9,'bold'))
        
        #style.configure('TFrame', background='red')
        #style.configure('TLabelframe', background='red')
        #style.configure('TLabel', background='red')
        #style.configure('.', background='red')
    
    def build_menu(self, menu_definitions):
        menu_bar = tk.Menu(self.root)
        for definition in menu_definitions:
            menu = tk.Menu(menu_bar, tearoff=0)
            top_level_menu, pull_down_menus = definition.split('-')
            menu_items = map(str.strip, pull_down_menus.split(','))
            for item in menu_items:
                self._add_menu_command(menu, item)
            menu_bar.add_cascade(label=top_level_menu, menu=menu)
        self.root.config(menu=menu_bar)

    def _add_menu_command(self, menu, item):
        if item == 'sep':
            menu.add_separator()
        else:
            menu_label, accelrator_key, command_callback = item.split('/')
            try:
                underline = menu_label.index('&')
                menu_label = menu_label.replace('&', '', 1)
            except ValueError:
                underline = None
            menu.add_command(label=menu_label, underline=underline, accelerator=accelrator_key, command=eval(command_callback))
            
    # Array of Frames that is in the Notebook: Array of tabs.       
    def build_tabs(self, tabs_definition):
        self.tabs = [] # Frame
        for definition in tabs_definition:
            self.tabs.append(ttk.Frame(self.tabPages))
            self.tabPages.add(self.tabs[-1], text = definition)
        self.tabPages.hide(1)
        self.tabPages.pack(expand=1, fill="both")
    
    def newFile(self):
        pass
    
    def save_file(self):
        pass

    def save_as(self):
        pass

    def exitCalcTag(self):
        self.root.quit()
        self.root.destroy()
        exit()
    
    def setting(self):
        pass
    
    def offline(self):
        pass
    
    def show_urlExtractor(self):
        pass
    
    def show_GTM(self):
        self.GTM = not self.GTM
        if self.GTM:
            self.tabPages.add(self.tabs[1])
        else:
            self.tabPages.hide(1)
    
    def documentation(self):
        pass
    
    def aboutTagCalc(self):
        pass
    
class tagFrontEnd(FrameWork2D):
    def __init__(self, root, webDOM, xlsxFile, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.webDOM        = webDOM
        self.xlsxFile      = xlsxFile
        self.pathTR        = tk.StringVar()  
        self.urlAdvertiser = tk.StringVar()
        self.advertiser    = tk.StringVar()
        self.searchXML     = tk.BooleanVar()
        self.maxCategory   = tk.IntVar()
        self.minSizeWord   = tk.IntVar()
        self.maxLandings   = tk.IntVar()
        self._init_params()

    
    def _init_params(self):
        self.pathTR.set(self.xlsxFile.PATH)
        self.urlAdvertiser.set(self.webDOM.url_target)
        self.advertiser.set(self.xlsxFile.readCell('C13'))
        self.maxCategory.set(15)
        self.webDOM.setMaxCategories(self.maxCategory.get())
        self.minSizeWord.set(3)
        self.webDOM.setSizeWord(self.minSizeWord.get())
        self.maxLandings.set(50)
        self.webDOM.setMaxLandings(self.maxLandings.get())
        self.searchXML.set(False)
        self.webDOM.setSearchXML(self.searchXML.get())
        self.buildTab(0)

    # Function to build diferents tabs: Sitemap and GTM
    def buildTab(self, indexTab):
        self.createParameterSection(indexTab)
        self.createDataSection(indexTab)
        
    def loadTemple(self):
        self.pathTR.set(filedialog.askopenfilename(title = 'Select a Tagging Request Temple', filetypes=[('XLSX', '*.xlsx *.XLSX')]))
        self.xlsxFile.setPATH(self.pathTR.get())
        self.xlsxFile.setBook()
        self.xlsxFile.setSheet()
        self.advertiser.set(self.xlsxFile.readCell('C13'))
        
    def loadAdvertiser(self):
        pass
    
    def createParameterSection(self, indexTab):
        #Parameter Section
        parameters_label_frame = ttk.LabelFrame(self.tabs[indexTab], text='Parameters', width=780, height=100)
        parameters_frame       = ttk.Frame(parameters_label_frame)
        parameters_label_frame.grid(column = 0, row=0)
        parameters_label_frame.grid_propagate(0)
        
        parameters_frame.grid(column = 0, row=0)

        # ttk.Label(parameters_frame, text="Temple TR: ", style = 'BW.TLabel').grid(column=0, row=0)
        # ttk.Entry(parameters_frame, width=75, textvariable = self.pathTR).grid(column=1, row=0, columnspan=3)
        # ttk.Button(parameters_frame, text='...', command=self.loadTemple).grid(column=4, row=0)
        
        ttk.Label(parameters_frame, text="URL Target:").grid(column=0, row=0, sticky=tk.W)
        tk.Entry(parameters_frame, width=30, textvariable = self.urlAdvertiser, font=('Arial',8,'italic'), relief=tk.SUNKEN, borderwidth=2).grid(column=1, row=0, sticky=tk.W)
        ttk.Label(parameters_frame, text="Advertiser:").grid(column=2, row=0, sticky=tk.W)
        tk.Entry(parameters_frame, textvariable = self.advertiser, font=('Arial',8,'italic'), relief=tk.SUNKEN, borderwidth=2).grid(column=3, row=0, sticky=tk.W)
        ttk.Label(parameters_frame, text="Only HomePV:").grid(column=4, row=0, sticky=tk.W)
        ttk.Checkbutton(parameters_frame, command=self.set_search, variable=self.searchXML, onvalue=False, offvalue=True).grid(column=5, row=0)
        
        ttk.Label(parameters_frame, text="Max Categories:").grid(column=0, row=1, sticky=tk.W)
        self.maxCategories = ttk.Scale(parameters_frame, from_=10, to=50, command=self.set_maxCategories, variable=self.maxCategory)
        self.maxCategories.grid(column=1, row=2, sticky=tk.W)
        ttk.Label(parameters_frame, textvariable=self.maxCategory, font=('Arial',8,'italic')).grid(column=1, row=1, sticky=tk.W)

        ttk.Label(parameters_frame, text="Min. Size Word:").grid(column=2, row=1, sticky=tk.W)
        self.sizeWord = ttk.Scale(parameters_frame, from_=2, to=15, command=self.set_sizeWord, variable=self.minSizeWord)
        self.sizeWord.grid(column=3, row=2)
        self.sizeWord.set(3)
        ttk.Label(parameters_frame, textvariable=self.minSizeWord, font=('Arial',8,'italic')).grid(column=3, row=1, sticky=tk.W)

        ttk.Label(parameters_frame, text="Max. Landings:").grid(column=4, row=1, sticky=tk.W)
        self.landings = ttk.Scale(parameters_frame, from_=50, to=500, command=self.set_maxLandings, variable=self.maxLandings)
        self.landings.grid(column=5, row=2)
        self.landings.set(100)
        ttk.Label(parameters_frame, textvariable=self.maxLandings, font=('Arial',8,'italic')).grid(column=5, row=1, sticky=tk.W)
        #ttk.Button(parameters_frame, text='.').grid(column=4, row=1)
        
    def createDataSection(self, indexTab):
        data_label_frame  = ttk.LabelFrame(self.tabs[indexTab], text='Data', width=780, height=295)
        data_label_frame.grid(column = 0, row=1)
        data_label_frame.grid_propagate(0)
        # Frame's child data_label_frame
        self.data_table_frame  = ttk.Frame(data_label_frame, borderwidth=3, relief='ridge', width=780, height=230)
        self.data_table_frame.grid(column = 0, row=0)
        self.data_table_frame.grid_propagate(0)
        # Frame's child data_label_frame
        data_button_frame = ttk.Frame(data_label_frame)
        data_button_frame.grid(column = 0, row=1)
        
        self.btn_find = ttk.Button(data_button_frame, text='Find', command = self.find_threaded)
        self.btn_find.grid(column=0, row=0)

        self.btn_stop = ttk.Button(data_button_frame, text='Stop', command = self.stopSearch, state = 'disable')
        self.btn_stop.grid(column=1, row=0)

        self.btn_sections = ttk.Button(data_button_frame, text='Sections', command = self.draw_threaded, state = 'disable')
        self.btn_sections.grid(column=2, row=0)
        self.btn_save = ttk.Button(data_button_frame, text='Save', command = self.save_threaded, state = 'disable')
        self.btn_save.grid(column=3, row=0)
        
        ttk.Button(data_button_frame, text='exit', command = self.exitCalcTag).grid(column=4, row=0)
        
        self.createTableData()
        
    def createTableData(self):
        self.dataTable = ttk.Treeview(self.data_table_frame, columns=['Landing', 'Path'], selectmode='extended')
        self.dataTable.heading('#0', text='Section', anchor='w')
        self.dataTable.heading('Landing', text='Landing', anchor='w')
        self.dataTable.heading('Path', text='Path', anchor='w')
        self.dataTable.column('#0', stretch=True, width=140)
        self.dataTable.column('Landing', stretch=True, width=520)
        self.dataTable.column('Path', stretch=True, width=110)
        self.dataTable.bind("<KeyPress-Delete>",self.deleteBranch)
        #self.scrollbar = ttk.Scrollbar(self.data_table_frame, orient=tk.VERTICAL, command=self.dataTable.yview)
        #self.dataTable.configure(yscrollcommand=self.scrollbar.set)
        #self.scrollbar.grid(row=0, column=1, sticky='NS')

        #self.scrollbar_ = ttk.Scrollbar(self.data_table_frame, orient=tk.HORIZONTAL, command=self.dataTable.xview)
        #self.dataTable.configure(xscrollcommand=self.scrollbar_.set)
        #self.scrollbar_.grid(row=1, sticky='WE')

        self.dataTable.grid(column=0, row=0, sticky='NESW')
        
    def addItem(self, parent, itemID, data):
        try:
            self.dataTable.insert(parent, 'end', iid=itemID, text=data[0], values=data[1:])
            return True
        except:
            return False

    def addItemTreeView(self, arraySections):
        self.deleteItemsTreeView()
        index_section = 0
        idd = 0
        print("Numero de Secciones: "+str(len(arraySections)))
        print(self.webDOM.mainSections)
        for mainSection in self.webDOM.mainSections:
            if mainSection == '':
                if self.dataTable.exists('MainDomain'):
                    self.dataTable.item('MainDomain', values=[self.webDOM.getUrlTarget(),''])
                else:
                    self.addItem('', 'Main', ['/','',''])
                    self.addItem('Main', 'MainDomain', ['', self.webDOM.getUrlTarget(),''])
            else:
                print("Index Section: "+str(index_section))
                parent = '/'+mainSection
                self.addItem('', mainSection, [parent,'',''])
                for subDomain in arraySections[index_section]:
                    #iid = subDomain.split('/')[-2] + subDomain.split('/')[-3]
                    self.addItem(mainSection, idd,['', subDomain,''])
                    idd+=1
                index_section+=1
                
    def deleteItemsTreeView(self):
        for mainSection in self.webDOM.mainSections:
            if self.dataTable.exists(mainSection):
                try:
                    self.dataTable.delete(mainSection)
                except:
                    continue
        
    def createSectionSheets(self, mainSections):
        self.xlsxFile.setSheet('Sections')
        self.xlsxFile.writeCell('C13', self.advertiser.get(), ['left','center'])
        self.xlsxFile.writeCell('C31', 'Section')
        self.xlsxFile.writeCell('D31', 'Page View')
        self.xlsxFile.writeCell('G31', 'u/p')
        for mainSection in mainSections:
            mainSection_ = mainSection.replace('/','-')
            self.xlsxFile.duplicateSheet('Sections', mainSection_)
        self.xlsxFile.setSheet('Tagging Request')
        self.xlsxFile.sheet = self.xlsxFile.book['Tagging Request']
        self.xlsxFile.sheet.title = 'Home'

    def aligmentCells(self):
        pass
            
    def loadData(self, dataSections):
        index_sheet = 4
        print(len(dataSections))
        print(self.xlsxFile.book.sheetnames)
        for dataSection in dataSections:
            self.xlsxFile.setSheet(self.xlsxFile.book.sheetnames[index_sheet])
            nameSection = self.xlsxFile.book.sheetnames[index_sheet]
            nameSection = nameSection.split('-')
            self.webDOM.deleteItemList(nameSection, '')
            nameSection.sort(key=len, reverse=True)
            if len(nameSection)>1:
                nameSection = nameSection[0]+'-'+nameSection[1]
            else:
                nameSection = nameSection[0]
            self.xlsxFile.writeCell('E31', self.xlsxFile.getNameSection(self.advertiser.get(), nameSection))
            self.xlsxFile.loadList(dataSection, 'F30')
            index_sheet += 1
        self.xlsxFile.setSheet(self.xlsxFile.book.sheetnames[1])
        self.xlsxFile.loadList([self.urlAdvertiser.get()], 'F30')
        
    def find_threaded(self):
        thread = Thread(target = self.find)
        thread.start()
        
    def draw_threaded(self):
        thread = Thread(target = self.draw)
        thread.start()
        
    def save_threaded(self):
        thread = Thread(target = self.save)
        thread.start()

    def set_search(self):
        self.webDOM.setSearchXML(self.searchXML.get())
    
    def set_maxCategories(self, event=None):
        self.maxCategory.set(self.maxCategory.get())
        self.webDOM.setMaxCategories(self.maxCategory.get())

    def set_sizeWord(self, event=None):
        self.minSizeWord.set(self.minSizeWord.get())
        self.webDOM.setSizeWord(self.minSizeWord.get())
    
    def set_maxLandings(self, event=None):
        self.maxLandings.set(self.maxLandings.get())
        self.webDOM.setMaxLandings(self.maxLandings.get())

    def deleteBranch(self, event):
        for item_ in self.dataTable.selection():
            if self.dataTable.parent(item_)=='':
                print(self.dataTable.item(item_))
                print(self.dataTable.focus())
                index = self.webDOM.mainSections.index(self.dataTable.focus())
                print(self.webDOM.arraySections[index-1][:2])
                remove_ = list(self.dataTable.selection())
                remove_.remove(item_)
                self.dataTable.selection_remove(remove_)
                break
        for item_ in self.dataTable.selection():
            if self.dataTable.parent(item_)=='':
                print('You will delete a section!')
                index = self.webDOM.mainSections.index(self.dataTable.focus())
                if index>0:
                    for url in self.webDOM.arraySections[index-1]:
                        url_ = urlparse(url)
                        if url_ in self.webDOM.subDomains: self.webDOM.subDomains.remove(url_)
                    self.webDOM.mainSections.pop(index)
                    self.webDOM.arraySections.pop(index-1)
                    self.dataTable.delete(item_)
            else:
                section = self.dataTable.parent(item_)
                index = self.webDOM.mainSections.index(section)
                values = self.dataTable.item(item_,'values')
                if index>0:
                    url_ = urlparse(values[0])
                    if url_ in self.webDOM.subDomains: self.webDOM.subDomains.remove(url_)
                    self.webDOM.arraySections[index-1].remove(values[0])
                    self.dataTable.delete(item_)
                print('You will delete a item!')
        #self.dataTable.delete(s)
        print("Are you sure that perform this action?")
    
    def find(self):
        self.webDOM.setStop(False)
        self.btn_find.configure(state='disable')
        #self.maxCategories.configure(state='disable')
        self.btn_stop.configure(state='active')
        self.deleteItemsTreeView()
        exists_url, exists_sitemap = self.webDOM.buildSiteMap(self.urlAdvertiser.get())
        self.lanchPopUps('Landings', 'The process of find landings has finished!', 'Press "Ok" to exit.')
        if exists_url:
            self.lanchPopUps('Landings', 'The process of find landings has finished!', 'Press "Ok" to exit.')
        else:
            self.lanchPopUps('URL Error!', "The URL given not found or it's incorrect!", 'Press "Ok" to exit.')
        self.btn_find.configure(state='active')
        self.btn_sections.configure(state='active')
        #self.maxCategories.configure(state='active')
        
    def stopSearch(self):
        self.btn_stop.configure(state='disable')
        self.webDOM.setStop(True)
        self.btn_find.configure(state='active')
        self.btn_stop.configure(state='active')
    
    def deep(self):
        self.webDOM.deeperSubDomains()
        
    def draw(self):
        self.btn_sections.configure(state='disable')
        self.webDOM.getArraySections()
        self.addItemTreeView(self.webDOM.arraySections)
        self.btn_sections.configure(state='active')
        self.btn_save.configure(state='active')
        self.lanchPopUps('Sectioned', 'The process of categorized has finished!', 'Press "Ok" to exit.')
        
    def validsSections(self, mainSections, arraySections):
        sections = []
    
    def save(self):
        self.btn_save.configure(state='disable')
        self.xlsxFile.setPATH(self.pathTR.get())
        self.xlsxFile.setBook()
        self.xlsxFile.setSheet()
        self.xlsxFile.writeCell('C13', self.advertiser.get(), ['left','center'])
        self.createSectionSheets(self.webDOM.mainSections[1:])
        self.xlsxFile.setSheet('Home')
        self.xlsxFile.writeCell('C31', 'Home')
        self.xlsxFile.writeCell('D31', 'Page View')
        self.xlsxFile.writeCell('G31', 'u')
        self.xlsxFile.writeCell('E31', self.xlsxFile.getNameSection(self.advertiser.get(), 'Home'))
        self.loadData(self.webDOM.arraySections)
        self.xlsxFile.book.remove(self.xlsxFile.book['Sections'])
        directory = filedialog.askdirectory()
        if len(directory) > 0:
            self.xlsxFile.saveBook(directory)
        else:
            self.xlsxFile.saveBook()
        self.btn_save.configure(state='active')
        self.lanchPopUps('Save', 'The TagCalc file has saved!', 'Press "Ok" to exit.')
        
    def lanchPopUps(self, title_, message_, detail_):
        messagebox.showinfo(
            title   = title_,
            message = message_,
            detail  = detail_
            )
        
    def exitCalcTag(self):
        self.webDOM.tearDown()
        self.root.quit()
        self.root.destroy()
        exit()
              
if __name__ == '__main__':
    root = tk.Tk()
    tagCalc = tagFrontEnd(root)
    tagCalc.mainloop()
