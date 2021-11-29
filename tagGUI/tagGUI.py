import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from threading import Thread

from os import path as p

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
        #785x400+300+100
        self.root.geometry("795x400+300+100")
        self.root.resizable(False,True)
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
##        style.configure('TFrame', background='red')
##        style.configure('TLabelframe', background='red')
##        style.configure('TLabel', background='red')
##        style.configure('.', background='red')
    
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
        self.webDOM     = webDOM
        self.xlsxFile   = xlsxFile
        self.pathTR = tk.StringVar()
        self.pathTR.set(self.xlsxFile.PATH)
        self.urlAdvertiser = tk.StringVar()
        self.urlAdvertiser.set(self.webDOM.url_target)
        self.advertiser = tk.StringVar()
        self.advertiser.set(self.xlsxFile.readCell('C13'))
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

        ttk.Label(parameters_frame, text="Temple TR: ", style = 'BW.TLabel').grid(column=0, row=0)
        ttk.Entry(parameters_frame, width=75, textvariable = self.pathTR).grid(column=1, row=0, columnspan=3)
        ttk.Button(parameters_frame, text='...', command=self.loadTemple).grid(column=4, row=0)
        
        ttk.Label(parameters_frame, text="URL Target : ").grid(column=0, row=1)
        ttk.Entry(parameters_frame, textvariable = self.urlAdvertiser).grid(column=1, row=1, columnspan=3, sticky='WE')
        #ttk.Button(parameters_frame, text='.').grid(column=4, row=1)
        
        ttk.Label(parameters_frame, text="Advertiser : ").grid(column=0, row=2)
        ttk.Entry(parameters_frame, textvariable = self.advertiser).grid(column=1, row=2, sticky=tk.W)
        
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
#         self.btn_stop = ttk.Button(data_button_frame, text='Stop', command = self.stopSearch, state = 'disable')
#         self.btn_stop.grid(column=1, row=0)
        self.btn_sections = ttk.Button(data_button_frame, text='Sections', command = self.draw_threaded, state = 'disable')
        self.btn_sections.grid(column=2, row=0)
        self.btn_save = ttk.Button(data_button_frame, text='Save', command = self.save_threaded, state = 'disable')
        self.btn_save.grid(column=3, row=0)
        
        ttk.Button(data_button_frame, text='exit', command = self.exitCalcTag).grid(column=4, row=0)
        
        self.createTableData()
        
    def createTableData(self):
        self.dataTable = ttk.Treeview(self.data_table_frame, columns=['Landing', 'Path'], selectmode='none')
        self.dataTable.heading('#0', text='Section', anchor='w')
        self.dataTable.heading('Landing', text='Landing', anchor='w')
        self.dataTable.heading('Path', text='Path', anchor='w')
        self.dataTable.column('#0', stretch=True, width=140)
        self.dataTable.column('Landing', stretch=True, width=520)
        self.dataTable.column('Path', stretch=True, width=110)
        
##        self.scrollbar = ttk.Scrollbar(self.data_table_frame, orient=tk.VERTICAL, command=self.dataTable.yview)
##        self.dataTable.configure(yscrollcommand=self.scrollbar.set)
##        self.scrollbar.grid(row=0, column=1, sticky='NS')

##        self.scrollbar_ = ttk.Scrollbar(self.data_table_frame, orient=tk.HORIZONTAL, command=self.dataTable.xview)
##        self.dataTable.configure(xscrollcommand=self.scrollbar_.set)
##        self.scrollbar_.grid(row=1, sticky='WE')
        
        self.dataTable.grid(column=0, row=0, sticky='NESW')
        
    def addItem(self, parent, itemID, data):
        try:
            self.dataTable.insert(parent, 'end', iid=itemID, text=data[0], values=data[1:])
            return True
        except:
            return False
        
#         for child in self.tabs[indexTab].winfo_children():
#             child.grid_configure(sticky='W')

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
                parent = r'/'+mainSection
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
        for mainSection in mainSections:
            mainSection_ = mainSection.replace('/','-')
            self.xlsxFile.duplicateSheet(self.xlsxFile.book.sheetnames[1], mainSection_)
        self.xlsxFile.sheet = self.xlsxFile.book['Tagging Request']
        self.xlsxFile.sheet.title = 'Home'
            
    def loadData(self, dataSections):
        index_sheet = 3
        print(len(dataSections))
        print(self.xlsxFile.book.sheetnames)
        for dataSection in dataSections:
            self.xlsxFile.setSheet(self.xlsxFile.book.sheetnames[index_sheet])
            self.xlsxFile.loadList(dataSection, 'G30')
            index_sheet += 1
        self.xlsxFile.setSheet(self.xlsxFile.book.sheetnames[1])
        self.xlsxFile.loadList([self.urlAdvertiser.get()], 'G30')
        
    def find_threaded(self):
        thread = Thread(target = self.find)
        thread.start()
        
    def draw_threaded(self):
        thread = Thread(target = self.draw)
        thread.start()
        
    def save_threaded(self):
        thread = Thread(target = self.save)
        thread.start()

    def find(self):
        self.btn_find.configure(state='disable')
        self.deleteItemsTreeView()
        exists_url, exists_sitemap = self.webDOM.buildSiteMap(self.urlAdvertiser.get())
        self.btn_find.configure(state='active')
        self.btn_sections.configure(state='active')
        self.lanchPopUps('Landings', 'The process of find landings has finished!', 'Press "Ok" to exit.')
        if exists_url:
            self.lanchPopUps('Landings', 'The process of find landings has finished!', 'Press "Ok" to exit.')
        else:
            self.lanchPopUps('URL Error!', "The URL given not found or it's incorrect!", 'Press "Ok" to exit.')
        
    def stopSearch(self):
        pass
    
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
        self.xlsxFile.writeCell('C13', self.advertiser.get())
        self.createSectionSheets(self.webDOM.mainSections[1:])
        self.loadData(self.webDOM.arraySections)
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
