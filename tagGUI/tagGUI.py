import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from threading import Thread
import time, sys
import json
import re

from os import closerange, path as p
from urllib.parse import urlparse
from tkinter import font
from tkinter.constants import OFF

from tagModules.pixelBot import pixelBot

MENU_DEFINITION = (
            'File- &New/Ctrl+N/self.newFile, Save/Ctrl+S/self.save_file, SaveAs/Ctrl+Shift+S/self.save_as, sep, Exit/Ctrl+Q/self.exitCalcTag',
            'Edit- Setting/Ctrl+Z/self.setting, sep, Show Offline/Alt+F5/self.offline',
            'View- SiteMap Builder//self.show_siteMapTab, Pixel Creator//self.show_PixelTab, GTM Integrator//self.show_GTMTab, CAPI Integrator//self.show_CAPITab',
            'Help- Documentation/F2/self.documentation, About/F1/self.aboutTagCalc'
        )

LOGIN_PAGES     = (
    'https://invest.xandr.com/', 
    'https://displayvideo.google.com/',
    'https://ads.taboola.com/',
    'https://amerminsights.mplatform.com/',
    'https://tagmanager.google.com/',
    'https://business.facebook.com/latest/home'
)

TABS_DEFINITION = (
    'SiteMap',
    'Pixels',
    'GTM',
    'CAPI'
    )

SPECIAL_CELLS   = (
    'C31', 'D31', 'G31'
)

MONTHS          = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
]

PROGRAM_NAME = 'TagBuilder'

class FrameWork2D(ttk.Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = root
        self.tabPages = ttk.Notebook(self.root)
        self.build_menu(MENU_DEFINITION)
        self.build_tabs(TABS_DEFINITION)
        self.sitemapTab = True
        self.pixelTab   = False
        self.GTMTab     = False
        self.CAPITab    = False
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
        for index in range(1,len(tabs_definition)):
            self.tabPages.hide(index)
        #self.tabPages.hide(1)
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
    
    def show_siteMapTab(self):
        self.sitemapTab = not self.sitemapTab
        if self.sitemapTab:
            self.tabPages.add(self.tabs[0])
            self.tabPages.select(0)
        else:
            self.tabPages.hide(0)
    
    def show_PixelTab(self):
        self.pixelTab = not self.pixelTab
        if self.pixelTab:
            self.tabPages.add(self.tabs[1])
            self.tabPages.select(1)
        else:
            self.tabPages.hide(1)
            
    def show_GTMTab(self):
        self.GTMTab = not self.GTMTab
        if self.GTMTab:
            self.tabPages.add(self.tabs[2])
            self.tabPages.select(2)
        else:
            self.tabPages.hide(2)
    
    def show_CAPITab(self):
        self.CAPITab = not self.CAPITab
        if self.CAPITab:
            self.tabPages.add(self.tabs[3])
            self.tabPages.select(3)
        else:
            self.tabPages.hide(3)
    
    def documentation(self):
        pass
    
    def aboutTagCalc(self):
        pass
    
class tagFrontEnd(FrameWork2D):
    def __init__(self, root, webDOM, xlsxFile, pixelBot, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.webDOM        = webDOM
        self.xlsxFile      = xlsxFile
        self.pixelBot      = pixelBot
        self.arrayPixels   = []
        self.xandrSeg      = []
        self.xandrConv     = []
        self.DV360         = []
        self.minsights     = []
        self.taboolaSeg    = []
        self.taboolaConv   = []
        self.pathTR        = tk.StringVar()  
        self.directoryTR   = tk.StringVar()
        self.urlAdvertiser = tk.StringVar()
        self.advertiser    = tk.StringVar()
        self.advertiser_   = tk.StringVar()
        self.advertiserId  = tk.StringVar()
        self.searchXML     = tk.BooleanVar()
        self.show_         = tk.BooleanVar()
        self.seleniumDelay = tk.IntVar()
        self.users         = [tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()]
        self.passwords     = [tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()]
        self.maxCategory   = tk.IntVar()
        self.minSizeWord   = tk.IntVar()
        self.maxLandings   = tk.IntVar()
        self.viewProgress  = tk.IntVar()
        self.pixelProgress = tk.IntVar()
        self.GTM_ID        = tk.StringVar()
        self._init_params()
        self._set_credentials_threaded()

    def _init_params(self):
        self.pathTR.set(self.xlsxFile.PATH)
        self.directoryTR.set("")
        self.urlAdvertiser.set(self.webDOM.url_target)
        self.advertiser.set(self.xlsxFile.readCell('C13'))
        self.advertiser_.set('')
        self.advertiserId.set(self.xlsxFile.readCell('C14')) #'1971197'
        self.maxCategory.set(15)
        self.webDOM.setMaxCategories(self.maxCategory.get())
        self.minSizeWord.set(3)
        self.webDOM.setSizeWord(self.minSizeWord.get())
        self.maxLandings.set(50)
        self.webDOM.setMaxLandings(self.maxLandings.get())
        self.searchXML.set(False)
        self.show_.set(False)
        self.webDOM.setSearchXML(self.searchXML.get())
        self.viewProgress.set(0)
        self.pixelProgress.set(0)
        self.GTM_ID.set(self.xlsxFile.readCell('C23'))
        self.codeVerify = None
        self.closeTopW  = False
        for user, passwd in zip(self.users,self.passwords):
            user.set("")
            passwd.set("")
        self.setWindow = tk.Toplevel()
        self.setWindow.destroy()
        for index in range(len(TABS_DEFINITION)):
            self.buildTab(index)
    
    """
    This function allows to get the DSP's credentials without
    blocking the main GUI at the start the program TagCalc.
        Return:
            None: None
    """
    def _set_credentials_threaded(self):
        thread = Thread(target=self._set_credentials)
        thread.start()
    
    """
    This function initialize the credentials of the DSP Platforms.
        Return:
            None: None
    """
    def _set_credentials(self):
        try:
            print('hemos encontrado el archivo')
            with open('platform_credentials.json') as credentials_file:
                credentials = json.load(credentials_file)
                self.users[0].set(credentials['user'])
                for passwd, password in zip(credentials['passwords'].values(), self.passwords):
                    password.set(passwd)
        except FileNotFoundError:
            print('No hay archivo de credenciales')
            while not self.existAllCredentials() or self.setWindow.winfo_exists():
                if not self.setWindow.winfo_exists():
                    self.settingWindow() 
        except:
            pass 
        # print('hemos terminado de introducir las credenciales de logueo')
        # print(self.users[0].get())
        # print(self.passwords[0].get())
        # print(self.passwords[1].get())
        # print(self.passwords[2].get())

    def existAllCredentials(self):
        if self.users[0].get() == "":
            return False
        #for user, passwd in zip(self.users,self.passwords):
        for passwd in self.passwords:
            # if user.get() == "":
            #     return False
            if passwd.get() == "":
                return False
        else:
            return True

    """
    This function valid if a string is or not a URL valid.
        Return:
            Boolean: True or False
    """
    def validURL(self, url):
        url_ = re.compile(r"^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$")
        if url_.search(url) == None:
            return False
        else:
            return True
    
    """
    This function valid if a advertiser Name field is valid or not.
        Return:
            Boolean: True or False
    """   
    def validAdvertiserName(self):
        if self.advertiser.get() == '' or self.advertiser.get().casefold() == 'none' or self.advertiser.get() == None:
            return False
        else:
            return True

    """
    This function valid if a advertiser ID field is valid or not.
        Return:
            Boolean: True or False
    """    
    def validAdvertiserID(self):
        if self.advertiserId.get().isdigit():
            return True
        else:
            return False
   
    """
    This function valid if a Container ID field is valid or not.
        Return:
            Boolean: True or False
    """     
    def validGTMID(self):
        if self.GTM_ID.get() == '' or self.GTM_ID.get() == None or self.GTM_ID.get().casefold() == 'None':
            return False
        else:
            return True

    # Function to build diferents tabs: Sitemap and GTM
    def buildTab(self, indexTab):
        if   indexTab == 0:
            self.createParameterSection(indexTab)
            self.createDataSection(indexTab)
        elif indexTab == 1:
            self.createParameterSection(indexTab)
            self.createPixelSection(indexTab)
        elif indexTab == 2:
            self.createParameterSection(indexTab)
            self.createGTMSection(indexTab)
        elif indexTab == 3:
            self.createParameterSection(indexTab)
            self.createCAPISection(indexTab)
        
    def loadTemple(self):
        self.pathTR.set(filedialog.askopenfilename(title = 'Select a Tagging Request Temple', filetypes=[('XLSX', '*.xlsx *.XLSX')]))
        self.xlsxFile.setPATH(self.pathTR.get())
        self.xlsxFile.setBook()
        self.xlsxFile.setSheet()
        self.advertiser.set(self.xlsxFile.readCell('C13'))
        
    def loadTR(self):
        self.btn_create.configure(state='disable')
        self.btn_save_pixels.configure(state='disable')
        tempDir = filedialog.askopenfilename(title = 'Select a Tagging Request Temple', filetypes=[('XLSX', '*.xlsx *.XLSX')])
        try:
            if tempDir.split('/')[-1].startswith('TagReq_') and (tempDir.split('/')[-1][-12:-9] in MONTHS) and tempDir.split('/')[-1][-9:-5].isnumeric():
                self.directoryTR.set(tempDir)
                self.xlsxFile.setPATH(self.directoryTR.get())
                self.xlsxFile.setBook()
                self.xlsxFile.setSheet('Home')
                self.advertiser_.set(self.xlsxFile.readCell('C13'))
                self.advertiserId.set(self.xlsxFile.readCell('C14'))
            else:
                self.lanchPopUps('Invalid File', 'You must choice a valid file!', 'Press "Ok" to exit.')
        except:
            self.lanchPopUps('Invalid File', 'You must choice a valid file!', 'Press "Ok" to exit.')
        
    def setTemple(self):
        self.xlsxFile.setPATH(self.pathTR.get())
        self.xlsxFile.setBook()
        self.xlsxFile.setSheet()
        
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
        
        if indexTab == 0:
            ttk.Label(parameters_frame, text="URL Target:").grid(column=0, row=0, sticky=tk.W)
            tk.Entry(parameters_frame, width=30, textvariable = self.urlAdvertiser, font=('Arial',8,'italic'), relief=tk.SUNKEN, borderwidth=2).grid(column=1, row=0, sticky=tk.W)
            ttk.Label(parameters_frame, text="Advertiser:").grid(column=2, row=0, sticky=tk.W)
            tk.Entry(parameters_frame, textvariable = self.advertiser, font=('Arial',8,'italic'), relief=tk.SUNKEN, borderwidth=2).grid(column=3, row=0, sticky=tk.W)
            ttk.Label(parameters_frame, text='Advertiser ID:').grid(column=4, row=0, sticky=tk.W)
            tk.Entry(parameters_frame, textvariable=self.advertiserId, font=('Arial',8,'italic'), relief=tk.SUNKEN, borderwidth=2).grid(column=5, row=0, sticky=tk.W)
            
            ttk.Label(parameters_frame, text="Container ID").grid(column=0, row=1, sticky=tk.W)
            tk.Entry(parameters_frame, width=30, textvariable = self.GTM_ID, font=('Arial',8,'italic'), relief=tk.SUNKEN, borderwidth=2).grid(column=1, row=1, sticky=tk.W)
            ttk.Label(parameters_frame, text="Progress:").grid(column=2, row=1, sticky=tk.W)
            self.progressbar = ttk.Progressbar(parameters_frame, variable=self.viewProgress, orient = tk.HORIZONTAL, length=125, maximum=100)
            self.progressbar.grid(column=3, row=1, sticky=tk.W)
            ttk.Label(parameters_frame, text="Only HomePV:").grid(column=4, row=1, sticky=tk.W)
            ttk.Checkbutton(parameters_frame, command=self.set_search, variable=self.searchXML, onvalue=False, offvalue=True).grid(column=5, row=1)
            
            # ttk.Label(parameters_frame, text="Max Categories:").grid(column=0, row=1, sticky=tk.W)
            # self.maxCategories = ttk.Scale(parameters_frame, from_=10, to=50, command=self.set_maxCategories, variable=self.maxCategory)
            # self.maxCategories.grid(column=1, row=2, sticky=tk.W)
            # ttk.Label(parameters_frame, textvariable=self.maxCategory, font=('Arial',8,'italic')).grid(column=1, row=1, sticky=tk.W)
    
            # ttk.Label(parameters_frame, text="Min. Size Word:").grid(column=2, row=1, sticky=tk.W)
            # self.sizeWord = ttk.Scale(parameters_frame, from_=2, to=15, command=self.set_sizeWord, variable=self.minSizeWord)
            # self.sizeWord.grid(column=3, row=2)
            # self.sizeWord.set(3)
            # ttk.Label(parameters_frame, textvariable=self.minSizeWord, font=('Arial',8,'italic')).grid(column=3, row=1, sticky=tk.W)
    
            # ttk.Label(parameters_frame, text="Max. Landings:").grid(column=4, row=1, sticky=tk.W)
            # self.landings = ttk.Scale(parameters_frame, from_=50, to=500, command=self.set_maxLandings, variable=self.maxLandings)
            # self.landings.grid(column=5, row=2)
            # self.landings.set(100)
            # ttk.Label(parameters_frame, textvariable=self.maxLandings, font=('Arial',8,'italic')).grid(column=5, row=1, sticky=tk.W)
            #ttk.Button(parameters_frame, text='.').grid(column=4, row=1)
        elif indexTab == 1:
            ttk.Label(parameters_frame, text="T. Request File: ", style = 'BW.TLabel').grid(column=0, row=0)
            tk.Entry(parameters_frame, width=75, textvariable = self.directoryTR, font=('Arial',8,'italic'), relief=tk.SUNKEN, borderwidth=2).grid(column=1, row=0, columnspan=4)
            ttk.Button(parameters_frame, text='...', command=self.loadTR, width=2).grid(column=5, row=0, sticky=tk.NW)  
            
            ttk.Label(parameters_frame, text='Advertiser: ').grid(column=0, row=1, sticky=tk.W) 
            tk.Entry(parameters_frame, textvariable = self.advertiser_, font=('Arial',8,'italic'), relief=tk.SUNKEN, borderwidth=2).grid(column=1, row=1, sticky=tk.W)     
            ttk.Label(parameters_frame, text= 'Advertiser ID: ').grid(column=2, row=1, sticky=tk.W)
            tk.Entry(parameters_frame, textvariable=self.advertiserId, font=('Arial',8,'italic'), relief=tk.SUNKEN, borderwidth=2).grid(column=3, row=1, sticky=tk.W) 
            ttk.Label(parameters_frame, text="Progress:").grid(column=4, row=1, sticky=tk.W)
            ttk.Progressbar(parameters_frame, variable=self.pixelProgress, orient = tk.HORIZONTAL, length=125, maximum=100).grid(column=5, row=1, sticky=tk.W)
            ttk.Label(parameters_frame, text='Agency: ').grid(column=0, row=2, sticky=tk.W)
            self.agencies = ttk.Combobox(parameters_frame, state='readonly', font=('Arial',8,'italic'))
            self.agencies['values'] = ['Xaxis', 'Ford', 'Colgate']
            self.agencies.set('Xaxis')
            self.agencies.grid(column=1, row=2)
            ttk.Label(parameters_frame, text='Market: ').grid(column=2, row=2, sticky=tk.W)
            self.countries = ttk.Combobox(parameters_frame, state='readonly', font=('Arial',8,'italic'))
            self.countries['values'] = ['Argentina', 'Brazil', 'Chile', 'Colombia', 'Ecuador', 'Mexico', 'Miami', 'Peru', 'Puerto Rico', 'Uruguay', 'Venezuela']
            self.countries.set('Colombia')
            self.countries.grid(column=3, row=2)
            ttk.Label(parameters_frame, text="Platform: ").grid(column=4, row=2, sticky=tk.W)
            self.platforms = ttk.Combobox(parameters_frame, state='readonly', font=('Arial',8,'italic'))
            self.platforms['values'] = ['Xandr Seg', 'Xandr Conv', 'DV360', 'Taboola Seg', 'Taboola Conv', 'Minsights']
            self.platforms.set('Xandr Seg')
            self.platforms.grid(column=5, row=2)
            #ttk.Checkbutton(parameters_frame, command=self.set_search, variable=self.searchXML, onvalue=False, offvalue=True).grid(column=5, row=1)
            
            # ttk.Label(parameters_frame, text='Xandr: ').grid(column=0, row=2, sticky=tk.W)
            # ttk.Checkbutton(parameters_frame, command=self.set_search, variable=self.searchXML, onvalue=False, offvalue=True).grid(column=1, row=2, sticky=tk.W)
            # ttk.Label(parameters_frame, text='DV360: ').grid(column=2, row=2, sticky=tk.W)
            # ttk.Checkbutton(parameters_frame, command=self.set_search, variable=self.searchXML, onvalue=False, offvalue=True).grid(column=3, row=2, sticky=tk.W)
            # ttk.Label(parameters_frame, text='Taboola: ').grid(column=4, row=2, sticky=tk.W)
            # ttk.Checkbutton(parameters_frame, command=self.set_search, variable=self.searchXML, onvalue=False, offvalue=True).grid(column=6, row=2, sticky=tk.W)
        elif indexTab == 2:
            pass
        elif indexTab == 3:
            pass   
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
        
    """
        This method implement de Pixels Area in the Pixels Tab.
        Make up by two Frames: Table to show Pixels details and
        Section we allocate the control buttons.
        Return:
            None:   None
    """ 
    def createPixelSection(self, indexTab):
        pixel_label_frame  = ttk.LabelFrame(self.tabs[indexTab], text='Pixels', width=780, height=295)
        pixel_label_frame.grid(column = 0, row=1)
        pixel_label_frame.grid_propagate(0)
        
        self.pixel_table_frame  = ttk.Frame(pixel_label_frame, borderwidth=3, relief='ridge', width=780, height=230)
        self.pixel_table_frame.grid(column = 0, row=0)
        self.pixel_table_frame.grid_propagate(0)
        # Frame's child data_label_frame
        pixel_button_frame = ttk.Frame(pixel_label_frame)
        pixel_button_frame.grid(column = 0, row=1)

        self.btn_pixels = ttk.Button(pixel_button_frame, text='Pixels', command = self.pixels_threaded)
        self.btn_pixels.grid(column=0, row=0)
        
        self.btn_create = ttk.Button(pixel_button_frame, text='Create', command = self.createPixels_threaded, state = 'disable')
        self.btn_create.grid(column=1, row=0)
        
        self.btn_save_pixels = ttk.Button(pixel_button_frame, text='Save', command = self.savePixels_threaded, state = 'disable')
        self.btn_save_pixels.grid(column=2, row=0)
        
        ttk.Button(pixel_button_frame, text='exit', command = self.exitCalcTag).grid(column=3, row=0)
        self.createTableData(1)
        
    def createGTMSection(self, indexTab):
        GTM_label_frame  = ttk.LabelFrame(self.tabs[indexTab], text='Tags', width=780, height=295)
        GTM_label_frame.grid(column = 0, row=1)
        GTM_label_frame.grid_propagate(0)
        
        self.GTM_table_frame  = ttk.Frame(GTM_label_frame, borderwidth=3, relief='ridge', width=780, height=230)
        self.GTM_table_frame.grid(column = 0, row=0)
        self.GTM_table_frame.grid_propagate(0)
        # Frame's child data_label_frame
        GTM_button_frame = ttk.Frame(GTM_label_frame)
        GTM_button_frame.grid(column = 0, row=1)

        self.btn_pixels = ttk.Button(GTM_button_frame, text='Login', command = self.GTM_threaded)
        self.btn_pixels.grid(column=0, row=0)
        
        self.btn_create = ttk.Button(GTM_button_frame, text='Create', command = self.createPixels_threaded, state = 'disable')
        self.btn_create.grid(column=1, row=0)
        
        self.btn_save_pixels = ttk.Button(GTM_button_frame, text='Save', command = self.savePixels_threaded, state = 'disable')
        self.btn_save_pixels.grid(column=2, row=0)
        
        ttk.Button(GTM_button_frame, text='exit', command = self.exitCalcTag).grid(column=3, row=0)
        self.createTableData(2)
    
    def createCAPISection(self, indexTab):
        CAPI_label_frame  = ttk.LabelFrame(self.tabs[indexTab], text='Events', width=780, height=295)
        CAPI_label_frame.grid(column = 0, row=1)
        CAPI_label_frame.grid_propagate(0)
        
        self.CAPI_table_frame  = ttk.Frame(CAPI_label_frame, borderwidth=3, relief='ridge', width=780, height=230)
        self.CAPI_table_frame.grid(column = 0, row=0)
        self.CAPI_table_frame.grid_propagate(0)
        # Frame's child data_label_frame
        CAPI_button_frame = ttk.Frame(CAPI_label_frame)
        CAPI_button_frame.grid(column = 0, row=1)

        self.btn_pixels = ttk.Button(CAPI_button_frame, text='Events', command = self.events_threaded)
        self.btn_pixels.grid(column=0, row=0)
        
        self.btn_create = ttk.Button(CAPI_button_frame, text='Create', command = self.createPixels_threaded, state = 'disable')
        self.btn_create.grid(column=1, row=0)
        
        self.btn_save_pixels = ttk.Button(CAPI_button_frame, text='Save', command = self.savePixels_threaded, state = 'disable')
        self.btn_save_pixels.grid(column=2, row=0)
        
        ttk.Button(CAPI_button_frame, text='exit', command = self.exitCalcTag).grid(column=3, row=0)
        self.createTableData(3)
    
    """This method implement a visualization field of data in the diferent funcionalities as Sitemap, Pixels, GTM and CAPI.
       Parameters:
            indexTab:   Index that corresponds to the funcionality in each that want to implement the visualization field.
       Return:
            None:   None
    """    
    def createTableData(self, indexTab=0):
        if indexTab == 0:
            self.dataTable = ttk.Treeview(self.data_table_frame, columns=['Landing', 'Path'], selectmode='extended')
            self.dataTable.heading('#0', text='Category', anchor='w')
            self.dataTable.heading('Landing', text='Landing', anchor='w')
            self.dataTable.heading('Path', text='Path', anchor='w')
            self.dataTable.column('#0', stretch=True, width=200)
            self.dataTable.column('Landing', stretch=True, width=450)
            self.dataTable.column('Path', stretch=True, width=120)
            self.dataTable.bind("<KeyPress-Delete>",self.deleteBranch)
            #self.scrollbar = ttk.Scrollbar(self.data_table_frame, orient=tk.VERTICAL, command=self.dataTable.yview)
            #self.dataTable.configure(yscrollcommand=self.scrollbar.set)
            #self.scrollbar.grid(row=0, column=1, sticky='NS')
            #self.scrollbar_ = ttk.Scrollbar(self.data_table_frame, orient=tk.HORIZONTAL, command=self.dataTable.xview)
            #self.dataTable.configure(xscrollcommand=self.scrollbar_.set)
            #self.scrollbar_.grid(row=1, sticky='WE')
            self.dataTable.grid(column=0, row=0, sticky='NESW')
        elif indexTab == 1:
            self.pixelTable = ttk.Treeview(self.pixel_table_frame, columns=['Pixel Name', 'Trigger', 'Variables', 'URL/PATH'], selectmode='extended')
            self.pixelTable.heading('#0', text='Category', anchor='w')
            self.pixelTable.heading('Pixel Name', text='Pixel Name', anchor='w')
            self.pixelTable.heading('Trigger', text='Trigger', anchor='w')
            self.pixelTable.heading('Variables', text='Variables', anchor='w')
            self.pixelTable.heading('URL/PATH', text='URL/PATH', anchor='w')
            self.pixelTable.column('#0', stretch=True, width=180)
            self.pixelTable.column('Pixel Name', stretch=True, width=260)
            self.pixelTable.column('Trigger', stretch=True, width=75)
            self.pixelTable.column('Variables', stretch=True, width=75)
            self.pixelTable.column('URL/PATH', stretch=True, width=180)
            self.pixelTable.bind("<KeyPress-Delete>",self.deleteBranch)
            self.pixelTable.grid(column=0, row=0, sticky='NESW')
        elif indexTab == 2:
            self.GTMTable = ttk.Treeview(self.GTM_table_frame, columns=['Tag Name', 'Trigger', 'Variables', 'URL/PATH'], selectmode='extended')
            self.GTMTable.heading('#0', text='Category', anchor='w')
            self.GTMTable.heading('Tag Name', text='Tag Name', anchor='w')
            self.GTMTable.heading('Trigger', text='Trigger', anchor='w')
            self.GTMTable.heading('Variables', text='Variables', anchor='w')
            self.GTMTable.heading('URL/PATH', text='URL/PATH', anchor='w')
            self.GTMTable.column('#0', stretch=True, width=180)
            self.GTMTable.column('Tag Name', stretch=True, width=260)
            self.GTMTable.column('Trigger', stretch=True, width=75)
            self.GTMTable.column('Variables', stretch=True, width=75)
            self.GTMTable.column('URL/PATH', stretch=True, width=180)
            self.GTMTable.bind("<KeyPress-Delete>",self.deleteBranch)
            self.GTMTable.grid(column=0, row=0, sticky='NESW')
        elif indexTab == 3:
            self.CAPITable = ttk.Treeview(self.CAPI_table_frame, columns=['Event Name', 'Trigger', 'Variables', 'URL/PATH'], selectmode='extended')
            self.CAPITable.heading('#0', text='Category', anchor='w')
            self.CAPITable.heading('Event Name', text='Event Name', anchor='w')
            self.CAPITable.heading('Trigger', text='Trigger', anchor='w')
            self.CAPITable.heading('Variables', text='Variables', anchor='w')
            self.CAPITable.heading('URL/PATH', text='URL/PATH', anchor='w')
            self.CAPITable.column('#0', stretch=True, width=180)
            self.CAPITable.column('Event Name', stretch=True, width=260)
            self.CAPITable.column('Trigger', stretch=True, width=75)
            self.CAPITable.column('Variables', stretch=True, width=75)
            self.CAPITable.column('URL/PATH', stretch=True, width=180)
            self.CAPITable.bind("<KeyPress-Delete>",self.deleteBranch)
            self.CAPITable.grid(column=0, row=0, sticky='NESW')

    def settingWindow(self):
        self.setWindow = tk.Toplevel(self.root)
        TITLE = PROGRAM_NAME+' Settings'
        self.setWindow.title(TITLE)
        self.setWindow.iconbitmap('xaxis32x32.ico')
        self.setWindow.geometry("600x430+300+100")
        #General Section
        general_label_frame = ttk.LabelFrame(self.setWindow, text='General', width=595, height=100)
        general_frame       = ttk.Frame(general_label_frame)
        general_label_frame.grid(column=0, row=0)
        general_label_frame.grid_propagate(0)
        general_frame.grid(column=0, row=0)
        #SiteMap Section
        sitemap_label_frame = ttk.LabelFrame(self.setWindow, text='SiteMap', width=595, height=100)
        sitemap_frame       = ttk.Frame(sitemap_label_frame)
        sitemap_label_frame.grid(column=0, row=1)
        sitemap_label_frame.grid_propagate(0)
        sitemap_frame.grid(column = 0, row=0)
        #Pixels Section
        pixels_label_frame = ttk.LabelFrame(self.setWindow, text='Pixels', width=595, height=100)
        pixels_frame       = ttk.Frame(pixels_label_frame)
        pixels_label_frame.grid(column=0, row=2)
        pixels_label_frame.grid_propagate(0)
        pixels_frame.grid(column = 0, row=0)
        #GTM Section
        gtm_label_frame = ttk.LabelFrame(self.setWindow, text='GTM', width=595, height=100)
        gtm_frame       = ttk.Frame(gtm_label_frame)
        gtm_label_frame.grid(column = 0, row=3)
        gtm_label_frame.grid_propagate(0)
        gtm_frame.grid(column = 0, row=0)
        #Buttons Section
        btn_frame       = ttk.Frame(self.setWindow)
        btn_frame.grid(column = 0, row=4)

        ttk.Label(general_frame, text='User: ').grid(column=0, row=0, sticky=tk.W)
        ttk.Label(general_frame, text='Xandr: ').grid(column=0, row=1, sticky=tk.W)
        ttk.Label(general_frame, text='DV360: ').grid(column=2, row=1, sticky=tk.W)
        ttk.Label(general_frame, text='Taboola: ').grid(column=4, row=1, sticky=tk.W)
        ttk.Label(general_frame, text='Minsights: ').grid(column=0, row=2, sticky=tk.W)
        ttk.Label(general_frame, text='Facebook: ').grid(column=2, row=2, sticky=tk.W)
        ttk.Label(general_frame, text='Show: ').grid(column=4, row=2, sticky=tk.W)
        tk.Entry(general_frame, textvariable=self.users[0], font=('Arial',8,'italic'), relief=tk.SUNKEN, borderwidth=2).grid(row=0, column=1, columnspan=3, sticky=tk.W)
        self.xandr_passwd = tk.Entry(general_frame, textvariable=self.passwords[0], show='*', font=('Arial',8,'italic'), relief=tk.SUNKEN, borderwidth=2)
        self.xandr_passwd.grid(column=1, row=1, sticky=tk.W)
        self.dv360_passwd = tk.Entry(general_frame, textvariable=self.passwords[1], show='*', font=('Arial',8,'italic'), relief=tk.SUNKEN, borderwidth=2)
        self.dv360_passwd.grid(column=3, row=1, sticky=tk.W)
        self.taboo_passwd = tk.Entry(general_frame, textvariable=self.passwords[2], show='*', font=('Arial',8,'italic'), relief=tk.SUNKEN, borderwidth=2)
        self.taboo_passwd.grid(column=5, row=1, sticky=tk.W)
        self.minsi_passwd = tk.Entry(general_frame, textvariable=self.passwords[3], show='*', font=('Arial',8,'italic'), relief=tk.SUNKEN, borderwidth=2)
        self.minsi_passwd.grid(column=1, row=2, sticky=tk.W)
        self.meta_passwd  = tk.Entry(general_frame, textvariable=self.passwords[4], show='*', font=('Arial',8,'italic'), relief=tk.SUNKEN, borderwidth=2)
        self.meta_passwd.grid(column=3, row=2, sticky=tk.W)
        ttk.Checkbutton(general_frame, command=self.show_credentials, variable=self.show_, onvalue=True, offvalue=False).grid(column=5, row=2, sticky=tk.W)
        
        ttk.Button(btn_frame, text='Save', command = self.saveSettings).grid(column=0, row=0)
        self.setExit = ttk.Button(btn_frame, text='exit', command = self.setWindow.destroy, state = 'disable')
        self.setExit.grid(column=1, row=0)
        
        """
            Sitemap Settings
        """
        ttk.Label(sitemap_label_frame, text='Schemes: ').grid(column=0, row=0, sticky=tk.W)
        self.schemes = ttk.Combobox(sitemap_label_frame, state='readonly', font=('Arial',8,'italic'))
        self.schemes['values'] = ['https', 'http', 'ftp']
        self.schemes.set('https')
        self.schemes.grid(column=1, row=0)
        ttk.Label(sitemap_label_frame, text='Build By: ').grid(column=2, row=0, sticky=tk.W)
        self.builtBy = ttk.Combobox(sitemap_label_frame, state='readonly', font=('Arial',8,'italic'))
        self.builtBy['values'] = ['path', 'fragment', 'query', 'parameters']
        self.builtBy.set('path')
        self.builtBy.grid(column=3, row=0)
        #MSD: Maximo Sections Desirable
        ttk.Label(sitemap_label_frame, text="MSD: ").grid(column=0, row=2, sticky=tk.W)
        self.maxCategories = ttk.Scale(sitemap_label_frame, from_=10, to=50, command=self.set_maxCategories, variable=self.maxCategory)
        self.maxCategories.grid(column=1, row=3, sticky=tk.W)
        ttk.Label(sitemap_label_frame, textvariable=self.maxCategory, font=('Arial',8,'italic')).grid(column=1, row=2, sticky=tk.W)
        #MPW: Minimo Path Word
        ttk.Label(sitemap_label_frame, text="MPW: ").grid(column=2, row=2, sticky=tk.W)
        self.sizeWord = ttk.Scale(sitemap_label_frame, from_=2, to=15, command=self.set_sizeWord, variable=self.minSizeWord)
        self.sizeWord.grid(column=3, row=3)
        self.sizeWord.set(3)
        ttk.Label(sitemap_label_frame, textvariable=self.minSizeWord, font=('Arial',8,'italic')).grid(column=3, row=2, sticky=tk.W)
        #Minimo URL Deserable
        ttk.Label(sitemap_label_frame, text="MUD: ").grid(column=4, row=2, sticky=tk.W)
        self.landings = ttk.Scale(sitemap_label_frame, from_=10, to=500, command=self.set_maxLandings, variable=self.maxLandings)
        self.landings.grid(column=5, row=3, sticky=tk.W)
        ttk.Label(sitemap_label_frame, textvariable=self.maxLandings, font=('Arial',8,'italic')).grid(column=5, row=2, sticky=tk.W)
        """
            GTM Pixels
        """
        ttk.Label(pixels_label_frame, text='Scroll Deep: ').grid(column=0, row=0, sticky=tk.W)
        self.scrollDeep = ttk.Combobox(pixels_label_frame, state='readonly', font=('Arial',8,'italic'))
        self.scrollDeep['values'] = ['30', '50', '70', '100']
        self.scrollDeep.set('50')
        self.scrollDeep.grid(column=1, row=0)
        ttk.Label(pixels_label_frame, text='Timer Last: ').grid(column=2, row=0, sticky=tk.W)
        self.builtBy = ttk.Combobox(pixels_label_frame, state='readonly', font=('Arial',8,'italic'))
        self.builtBy['values'] = ['30', '60', '120', '150']
        self.builtBy.set('30')
        self.builtBy.grid(column=3, row=0)
        self.seleniumDelay.set(30)
        ttk.Label(pixels_label_frame, text="Delay Execution: ").grid(column=0, row=2, sticky=tk.W)
        self.delaySelenium = ttk.Scale(pixels_label_frame, from_=10, to=240, command=self.set_seleniumDelay, variable=self.seleniumDelay)
        self.delaySelenium.grid(column=1, row=3, sticky=tk.W)
        ttk.Label(pixels_label_frame, textvariable=self.seleniumDelay, font=('Arial',8,'italic')).grid(column=1, row=2, sticky=tk.W)
        
    def set_seleniumDelay(self):
        pass
    
    def saveSettings(self):
        if self.existAllCredentials:
            self.setExit.configure(state='active')
        credentials = {'user':self.users[0].get(), 'passwords':{'Xandr':self.passwords[0].get(), 'DV360':self.passwords[1].get(), 'Taboola':self.passwords[2].get(), 'Minsights':self.passwords[3].get(), 'Meta':self.passwords[4].get()}}
        with open("platform_credentials.json", "w") as credentials_file:
            json.dump(credentials, credentials_file)  
            
    def show_credentials(self):
        if self.show_.get():
            self.xandr_passwd.configure(show='')
            self.dv360_passwd.configure(show='')
            self.taboo_passwd.configure(show='')
            self.minsi_passwd.configure(show='')
            self.meta_passwd.configure(show='')
        else:
            self.xandr_passwd.configure(show='*')
            self.dv360_passwd.configure(show='*')
            self.taboo_passwd.configure(show='*') 
            self.minsi_passwd.configure(show='*') 
            self.meta_passwd.configure(show='*')      
         
    def addItem(self, parent, itemID, data, numTree=0):
        if numTree == 0:
            try:
                self.dataTable.insert(parent, 'end', iid=itemID, text=data[0], values=data[1:])
                return True
            except:
                return False
        elif numTree == 1:
            try:
                self.pixelTable.insert(parent, 'end', iid=itemID, text=data[0], values=data[1:])
                return True
            except:
                return False

    def deleteItemsTreeView(self, numTree=0):
        if numTree == 0:
            for mainSection in self.webDOM.mainSections:
                if self.dataTable.exists(mainSection):
                    try:
                        self.dataTable.delete(mainSection)
                    except:
                        continue
        elif numTree == 1:
            for pixel in self.arrayPixels:
                if self.pixelTable.exists(pixel[0]):
                    try:
                        self.pixelTable.delete(pixel[0])
                    except:
                        continue

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
                    self.addItem('', 'Main', ['/Home','',''])
                    self.addItem('Main', 'MainDomain', ['', self.webDOM.getUrlTarget(),''])
            else:
                print("Index Section: "+str(index_section))
                parent = '/'+self.fitNameSection(mainSection)
                self.addItem('', mainSection, [parent,'',''])
                for subDomain in arraySections[index_section]:
                    #iid = subDomain.split('/')[-2] + subDomain.split('/')[-3]
                    self.addItem(mainSection, idd,['', subDomain,''])
                    idd+=1
                index_section+=1
                
    def addItemTreeViewII(self, arrayPixels):
        categories = []
        idd = 0
        self.deleteItemsTreeView(1)
        #self.arrayPixels = self.getArrayPixels()
        for pixel in arrayPixels:
            if pixel[0] not in categories:
                categories.append(pixel[0])
        time.sleep(10)
        for category in categories:
            self.addItem('', category, ['/'+category,'','','',''], 1)
            for pixel in arrayPixels:
                if pixel[0] == category:
                    self.addItem(category, idd, ['',pixel[1],pixel[2],pixel[3],pixel[4]], 1)
                idd+=1
        self.arrayPixels = arrayPixels
                
    def fitNameSection(self, nameSection):
        category = ''
        words = nameSection.split('/')
        self.webDOM.deleteItemList(words, '')
        if len(words)>1:
            if not words[0].isnumeric():
                words = words[0]
            else:
                words = words[1]
        else:
            words = words[0]
        #words = nameSection.replace('-', ' ')
        words = words.split('-')
        self.webDOM.deleteItemList(words, '')
        for word in words:
            if not word.isnumeric():
                category = category+word.capitalize()
        return category
        
    def createSectionSheets(self, mainSections):
        self.xlsxFile.setSheet('Sections')
        self.xlsxFile.writeCell('C13', self.advertiser.get(), ['left','center'])
        self.xlsxFile.writeCell('C31', 'Section')
        self.xlsxFile.writeCell('D31', 'Page View')
        self.xlsxFile.writeCell('G31', 'u/p')
        for mainSection in mainSections:
            #mainSection_ = mainSection.replace('/','-')
            mainSection_ = self.fitNameSection(mainSection)
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
        
    def pixels_threaded(self):
        #thread = Thread(target = self.loginAllPlatforms)
        thread = Thread(target = self.pixels)
        thread.start()
        
    def save_threaded(self):
        thread = Thread(target = self.save)
        thread.start()
        
    def savePixels_threaded(self):
        thread = Thread(target = self.savePixels)
        thread.start()

    def createPixels_threaded(self): 
        thread = Thread(target = self.createPixels)
        thread.start()
        
    def events_threaded(self):
        self.logInPlatform(LOGIN_PAGES[5], self.users[0].get(), self.passwords[4].get())
    
    def GTM_threaded(self):
        pass

    def updateCodeVerify_threaded(self):
        thread = Thread(target = self.updateCodeVerify)
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
        if self.validURL(self.urlAdvertiser.get()):
            self.webDOM.viewProgress = 1
            self.updateProgress_threaded()
            self.webDOM.setStop(False)
            self.btn_find.configure(state='disable')
            #self.maxCategories.configure(state='disable')
            self.btn_stop.configure(state='active')
            self.deleteItemsTreeView()
            existContainer, containerID = self.pixelBot.existGTM(self.urlAdvertiser.get())
            self.GTM_ID.set(containerID)
            exists_url, exists_sitemap = self.webDOM.buildSiteMap(self.urlAdvertiser.get())
            if exists_url:
                if exists_sitemap and len(self.webDOM.subDomains)>0:
                    self.lanchPopUps('Landings', 'The process of find landings has finished!', 'Press "Ok" to exit.')
                else:
                    self.webDOM.findAnchors()
                    self.webDOM.getSubDomains()
                    self.webDOM.deeperSubDomains()
                    exist_sitemap = True if len(self.webDOM.subDomains)>0 else False 
                    if exist_sitemap:
                        self.lanchPopUps('Landings', 'The process of find landings has finished!', 'Press "Ok" to exit.')
                    else:
                        self.lanchPopUps('Landings', 'TagBuilder does not find landings!', 'Press "Ok" to exit.')
            else:
                self.lanchPopUps('URL Error!', "The URL given not found or it's incorrect!", 'Press "Ok" to exit.')
            self.btn_find.configure(state='active')
            self.btn_sections.configure(state='active')
            self.webDOM.viewProgress = -1
            #self.maxCategories.configure(state='active')
        else:
            self.lanchPopUps('URL Error!', "The URL given is incorrect!", 'Press "Ok" to exit.')
        
    def stopSearch(self):
        self.btn_stop.configure(state='disable')
        self.webDOM.setStop(True)
        self.btn_find.configure(state='active')
        self.btn_stop.configure(state='active')
    
    def deep(self):
        self.webDOM.deeperSubDomains()
        
    def draw(self):
        self.btn_sections.configure(state='disable')
        if self.validAdvertiserName():
            self.webDOM.getArraySections()
            self.addItemTreeView(self.webDOM.arraySections)
            self.lanchPopUps('Sectioned', 'The process of categorized has finished!', 'Press "Ok" to exit.')
        else:
            self.lanchPopUps('Field Required!', 'The Advertiser Name is not valid!', 'Press "Ok" to exit.')
        self.btn_sections.configure(state='active')
        self.btn_save.configure(state='active')
        
    def createPixels(self):
        try:
            self.btn_create.configure(state='disable')
            if self.directoryTR.get() == '' or not self.advertiserId.get().isdigit() or self.advertiser_.get() == '' or self.advertiser_.get() == 'None':
                self.lanchPopUps('Incomplete Fields', 'Check the  fields:\n- T. Request File.\n- Advertiser.\n- Advertiser ID.', 'Press "Ok" to exit.')
            else:
                if self.platforms.get() == 'Xandr Seg' or self.platforms.get() == 'Xandr Conv':
                    self.pixelProgress.set(0)
                    pixelType = 'RTG' if self.platforms.get() == 'Xandr Seg' else 'CONV'
                    if self.logInPlatform(LOGIN_PAGES[0], self.users[0].get(), self.passwords[0].get()):
                        self.pixelProgress.set(2)
                        if not self.pixelBot.setMarketXandr(self.countries.get()): return self.lanchPopUps('Access', "You don't have access to this market", 'Press "Ok" to exit.') 
                        self.pixelProgress.set(5)
                        if self.pixelBot.existAdvertiserId(self.platforms.get(), self.advertiserId.get()):
                            progress = 0
                            self.pixelProgress.set(7)
                            self.xandrSeg, self.xandrConv = ([], self.xandrConv) if pixelType=='RTG' else (self.xandrSeg, [])
                            step = (7+83/len(self.arrayPixels)) if len(self.arrayPixels)>0 else 90
                            print('Initial Step:', step)
                            for pixel in self.arrayPixels:
                                if pixelType == 'RTG' and (pixel[6]==None or pixel[6]=='' or pixel[6]=='NO'):
                                    self.xandrSeg.append('')
                                elif pixelType == 'CONV' and (pixel[7]==None or pixel[7]=='' or pixel[7]=='NO'):
                                    self.xandrConv.append('')   
                                else:
                                    if not self.pixelBot.existPixel(self.platforms.get(), self.advertiserId.get(), pixel[1]):
                                        snippet =  self.pixelBot.createPixel(self.advertiserId.get(), pixel[1], platform=0, pixelType=pixelType)
                                        #pixel.append(snippet)
                                        self.xandrSeg.append(snippet) if pixelType=='RTG' else self.xandrConv.append(snippet)
                                    else:
                                        snippet = self.pixelBot.getSnippetCode(self.advertiserId.get(),pixel[1], self.platforms.get())
                                        self.xandrSeg.append(snippet) if pixelType=='RTG' else self.xandrConv.append(snippet)
                                        #pixel.append(snippet)
                                        self.lanchPopUps('Pixel Exists!', 'The pixel, %s, exists.'%pixel[1], 'Press "Ok" to exit.')
                                        #print('El pixel: '+pixel[1]+', existe y no se puede crear!!!')
                                progress += step
                                print('Intermediate Steps', progress)
                                self.pixelProgress.set(progress)
                            print('The snippet are: ')
                            print(self.xandrSeg)
                            print(self.xandrConv)
                            self.lanchPopUps('Finished', 'Process of create Pixels have already finished.', 'Press "Ok" to exit.')
                        else:
                            self.pixelProgress.set(0)
                            self.lanchPopUps('Not founded!', "The advertiser can't founded!", 'Press "Ok" to exit.')
                    else:
                        self.lanchPopUps('Xandr login failed!', 'Check your credentials, please.', 'Press "Ok" to exit.')
                elif self.platforms.get() == 'DV360':
                    self.pixelProgress.set(0)
                    if self.logInPlatform(LOGIN_PAGES[1], self.users[0].get(), self.passwords[1].get()):
                        self.pixelProgress.set(2)
                        if self.pixelBot.existAdvertiserId(self.platforms.get(), self.advertiserId.get()):
                            self.DV360 = []
                            progress = 0
                            self.pixelProgress.set(5)
                            step = (5+85/len(self.arrayPixels)) if len(self.arrayPixels)>0 else 90
                            for pixel in self.arrayPixels:
                                if pixel[8] in [None,'','No','NO','no', 'nO']:
                                    self.DV360.append('')
                                else:
                                    if not self.pixelBot.existPixel(self.platforms.get(), self.advertiserId.get(), pixel[1]):
                                        snippet =  self.pixelBot.createPixel(self.advertiserId.get(), pixel[1], platform=1)
                                        self.DV360.append(snippet)
                                        #pixel.append(snippet)
                                    else:
                                        snippet = self.pixelBot.getSnippetCode(self.advertiserId.get(),pixel[1], self.platforms.get())
                                        self.DV360.append(snippet)
                                        #pixel.append(snippet)
                                        self.lanchPopUps('Pixel Exists!', 'The pixel, %s, exists.'%pixel[1], 'Press "Ok" to exit.')
                                        #print('El pixel: '+pixel[1]+', existe y no se puede crear!!!')
                                progress += step
                                self.pixelProgress.set(progress)
                            print('The snippet are: ')
                            for pixel in self.DV360:
                                print(pixel)
                            self.lanchPopUps('Finished', 'Process of create Pixels have already finished.', 'Press "Ok" to exit.')
                        else:
                            self.pixelProgress.set(0)
                            self.lanchPopUps('Not founded!', "The advertiser can't founded!", 'Press "Ok" to exit.')
                    else:
                        self.lanchPopUps('DV360 login failed!', 'Check your credentials, please.', 'Press "Ok" to exit.')
                elif self.platforms.get() == 'Taboola Seg' or self.platforms.get() == 'Taboola Conv':
                    self.pixelProgress.set(0)
                    pixelType = 'RTG' if self.platforms.get() == 'Taboola Seg' else 'CONV'
                    if self.logInPlatform(LOGIN_PAGES[2], self.users[0].get(), self.passwords[2].get()):
                        self.pixelProgress.set(2)
                        if self.pixelBot.existAdvertiserId(self.platforms.get(), self.advertiserId.get()):
                            self.pixelProgress.set(5)
                            if self.pixelBot.existTaboolaPixel(self.advertiserId.get()):
                                progress = 0
                                self.pixelProgress.set(7)
                                step = (7+83/len(self.arrayPixels)) if len(self.arrayPixels)>0 else 90
                                self.taboolaSeg, self.taboolaConv = ([], self.taboolaConv) if pixelType=='RTG' else (self.taboolaSeg, [])
                                for pixel in self.arrayPixels:
                                    if pixelType == 'RTG' and pixel[9] in ['NO', 'No', 'no', 'nO', '', None]:
                                        self.taboolaSeg.append('')
                                    elif pixelType == 'CONV' and pixel[10] in ['NO', 'No', 'no', 'nO', '', None]:
                                        self.taboolaConv.append('')
                                    else:
                                        event   = True if (pixelType == 'RTG' and pixel[9] in ['Event', 'event', 'EVENT']) or (pixelType == 'CONV' and pixel[10] in ['Event', 'event', 'EVENT']) else False
                                        pathURL = pixel[4] if not event else None
                                        if self.pixelBot.existPixel(self.platforms.get(), self.advertiserId.get(), pixel[1]): self.lanchPopUps('Pixel Exists!', "The pixel %s already existed!"%pixel[1], 'Press "Ok" to exit.')
                                        snippet =  self.pixelBot.createPixel(self.advertiserId.get(), pixel[1], platform=2, pixelType=pixelType, event_=event, pathURL=pathURL)
                                        self.taboolaSeg.append(snippet) if pixelType=='RTG' else self.taboolaConv.append(snippet)
                                    progress += step
                                    self.pixelProgress.set(progress)
                                print('The snippet are: ')
                                print(self.taboolaSeg)
                                print(self.taboolaConv)
                                self.lanchPopUps('Finished', 'Process of create Pixels have already finished.', 'Press "Ok" to exit.')
                            else:
                                self.lanchPopUps('Universal Pixel!', "The Taboola Universal Pixel hasn't implemented yet!", 'Press "Ok" to exit.')
                                self.pixelProgress.set(0)
                        else:
                            self.lanchPopUps('Not founded!', "The advertiser can't founded!", 'Press "Ok" to exit.')
                            self.pixelProgress.set(0)
                    else:
                        self.lanchPopUps('Taboola login failed!', 'Check your credentials, please.', 'Press "Ok" to exit.')
                    #self.createPixel(self.platforms.get(), 'AllPagesTest', None)
                else:
                    self.pixelProgress.set(0)
                    if self.logInPlatform(LOGIN_PAGES[3], self.users[0].get(), self.passwords[3].get()):
                        self.pixelProgress.set(2)
                        minsightId = self.pixelBot.existMinsightsId(self.advertiser_.get(), self.countries.get(), self.agencies.get())
                        if minsightId != -1:
                            progress = 0
                            self.pixelProgress.set(5)
                            step = (7+83/len(self.arrayPixels)) if len(self.arrayPixels)>0 else 90
                            self.advertiserId.set(minsightId)
                            self.minsights = []
                            self.pixelProgress.set(7)
                            for pixel in self.arrayPixels:
                                if pixel[5] in [None,'','No','NO','no', 'nO', '']:
                                    self.minsights.append('')
                                else:
                                    if not self.pixelBot.existPixel(self.platforms.get(), self.advertiserId.get(), pixel[1]):
                                        #print('El pixel: '+pixel[1]+', no existe y se puede crear!!!')
                                        snippet =  self.pixelBot.createPixel(self.advertiserId.get(), pixel[1], platform=3, customVariable=pixel[3])
                                        self.minsights.append(snippet)
                                        #pixel.append(snippet)
                                    else:
                                        snippet = self.pixelBot.getSnippetCode(self.advertiserId.get(),pixel[1], self.platforms.get())
                                        self.minsights.append(snippet)
                                        #pixel.append(snippet)
                                        self.lanchPopUps('Pixel Exists!', 'The pixel, %s, exists.'%pixel[1], 'Press "Ok" to exit.')
                                        #print('El pixel: '+pixel[1]+', existe y no se puede crear!!!')
                                progress += step
                                self.pixelProgress.set(progress)
                            print('The snippet are: ')
                            for pixel in self.minsights:
                                print(pixel)
                            self.lanchPopUps('Finished', 'Process of create Pixels have already finished.', 'Press "Ok" to exit.')
                        else:
                            self.lanchPopUps('Not founded!', "The advertiser can't founded!", 'Press "Ok" to exit.')
                            self.pixelProgress.set(0)
                    else:
                        self.lanchPopUps('Minsights login failed!', 'Check your credentials, please.', 'Press "Ok" to exit.')
            self.btn_create.configure(state='active')
            self.btn_save_pixels.configure(state='active')
        except:
            self.lanchPopUps('Error!', str(sys.exc_info()[1]), 'Press "Ok" to exit.')
            self.btn_create.configure(state='active')
        
    def createPixel(self, platform_, pixelName_, variables):
        if platform_ == 'Xandr Seg':
            if self.advertiserId.get() != '' and self.advertiserId.get().isnumeric():
                snippet = self.pixelBot.createPixel(self.advertiserId.get(), pixelName_)
                #Add validation of snippet code and then to continue with following instructions
                self.xlsxFile.setPATH(self.directoryTR.get())
                self.xlsxFile.setBook()
                self.xlsxFile.setSheet('Home')
                self.xlsxFile.writeCell('J31',snippet)
                self.xlsxFile.saveBook()
                print(snippet)
            else:
                print('revise el Advertiser ID')
        elif platform_ == 'Xandr Conv':
            if self.advertiserId.get() != '' and self.advertiserId.get().isnumeric():
                snippet = self.pixelBot.createPixel(self.advertiserId.get(), pixelName_, pixelType='CONV')
                #Add validation of snippet code and then to continue with following instructions
                self.xlsxFile.setPATH(self.directoryTR.get())
                self.xlsxFile.setBook()
                self.xlsxFile.setSheet('Home')
                self.xlsxFile.writeCell('J31',snippet)
                self.xlsxFile.saveBook()
                print(snippet)
            else:
                print('revise el Advertiser ID')
        elif platform_ == 'DV360':
            if self.advertiserId.get() != '' and self.advertiserId.get().isnumeric():
                snippet = self.pixelBot.createPixel(self.advertiserId.get(), pixelName_, 1)
                #Add validation of snippet code and then to continue with following instructions
                self.xlsxFile.setPATH(self.directoryTR.get())
                self.xlsxFile.setBook()
                self.xlsxFile.setSheet('Home')
                self.xlsxFile.writeCell('J31',snippet)
                self.xlsxFile.saveBook()
                print(snippet)
            else:
                print('revise el Advertiser ID')
        elif platform_ == 'Taboola':
            if self.advertiserId.get() != '' and self.advertiserId.get().isnumeric():
                snippet = self.pixelBot.createPixel(self.advertiserId.get(), pixelName_, 2, pixelType='CONV')
                #Add validation of snippet code and then to continue with following instructions
                self.xlsxFile.setPATH(self.directoryTR.get())
                self.xlsxFile.setBook()
                self.xlsxFile.setSheet('Home')
                self.xlsxFile.writeCell('J31',snippet)
                self.xlsxFile.saveBook()
                print(snippet)
            else:
                print('revise el Advertiser ID')
        elif platform_ == 'Minsights':
            pass
     
    def createPixelsAll(self):
        while not self.existAllCredentials() or self.setWindow.winfo_exists():
            if not self.setWindow.winfo_exists():
                self.settingWindow()  
        for platform, user, password in zip(LOGIN_PAGES, self.users, self.passwords):
            login = False
            self.pixelBot.setDriver(platform)
            self.windowCode = False
            try_ = 0
            while True:
                login = self.pixelBot.doLogin(user.get(), password.get())
                if self.pixelBot.reqCode and (not self.windowCode): 
                    self.updateCodeVerify_threaded()
                    self.windowCode = True
                self.pixelBot.authFail = self.pixelBot.auth_alert()
                if login or self.pixelBot.authFail:
                    if self.pixelBot.authFail:
                        print('Ha habido un problema de authenticación')
                        if try_<2:
                            self.pixelBot.setDriver(platform)
                            try_+=3
                        else:
                            print('Ha habido un problema de authenticación')
                            break
                    else:
                        break
                elif self.pixelBot.approve:
                    print('Aprueba el ingreso por favor')
                elif not login and not self.pixelBot.startLog:
                    break
    
    """
        This method implement de Log-In Xandr platform.
        Return:
            LogIn:  Boolean
    """         
    def logInPlatform(self, loginPage, user, password):
        login = False
        windowCode = False
        try_ = 0
        self.pixelBot.setDriver(loginPage)
        while not login:
            login = self.pixelBot.doLogin(user, password)
            #self.pixelBot.authFail = self.pixelBot.auth_alert()
            if self.pixelBot.approve:
                self.lanchPopUps('Authorize', 'Authoriza the Access from your cellphone!', 'Press "Ok" to exit.')
                self.pixelBot.approve = False
            elif self.pixelBot.reqCode and not windowCode and self.pixelBot.isVerifyPage():
                windowCode = True
                self.updateCodeVerify_threaded()
                #self.updateCodeVerify()
            elif self.pixelBot.auth_alert(time_=2):
                if try_<2:
                    self.pixelBot.setDriver(loginPage)
                    windowCode = False
                    try_+=1
                else:
                    self.lanchPopUps('Auth Failed', 'There was a authentication problem!', 'Press "Ok" to exit.')
                    break
            elif not login and not self.pixelBot.startLog:
                break
        return login
    
    def loginAllPlatforms(self):
        self.logInPlatform(LOGIN_PAGES[0], self.users[0].get(), self.passwords[0].get())
        self.logInPlatform(LOGIN_PAGES[1], self.users[0].get(), self.passwords[1].get())
        self.logInPlatform(LOGIN_PAGES[2], self.users[0].get(), self.passwords[2].get())
        self.logInPlatform(LOGIN_PAGES[3], self.users[0].get(), self.passwords[3].get())

    def updateCodeVerify(self):
        alertWin = tk.Tk()
        alertWin.withdraw()
        self.pixelBot.code = simpledialog.askstring('Verification','What is the code?',parent=alertWin)
        alertWin.destroy()
    
    def validsSections(self, mainSections, arraySections):
        sections = []

    """This function get the parameters of the pixels to implement from TR file.
            Parameters:
                None:   None.
            Return:
                None: None. 
    """
    def pixels(self):
        self.btn_pixels.configure(state='disable')
        if self.validTRFile():
            #self.arrayPixels = self.getArrayPixels()
            self.addItemTreeViewII(self.getArrayPixels())
            self.lanchPopUps('Extracted!', 'The pixels had read from TR!', 'Press "Ok" to exit.')
        else:
            self.lanchPopUps('Invalid File', 'You must choice a valid file!', 'Press "Ok" to exit.')
        self.btn_create.configure(state='active')
        self.btn_pixels.configure(state='active')

    """This function valid if the directory in the flied TR. File is valid.
            Parameters:
                None:   None.
            Return:
                Boolean: True or False. 
    """
    def validTRFile(self):
        try:
            if self.directoryTR.get().split('/')[-1].startswith('TagReq_') and (self.directoryTR.get().split('/')[-1][-12:-9] in MONTHS) and self.directoryTR.get().split('/')[-1][-9:-5].isnumeric():
                return True
            else:
                return False
        except:
            return False
    
    """This function reads the TR file and get the differents pixels that we need to implement.
            Parameters:
                None:   None.
            Return:
                Pixels: Array of information about all pixels to implement. 
    """
    def getArrayPixels(self):
        pixels = []
        for sheetname in self.xlsxFile.book.sheetnames:
            self.xlsxFile.setSheet(sheetname)
            if sheetname == 'Concept Tagging Request ' or sheetname == 'Hoja1' or sheetname == 'Otros':
                continue
            if sheetname == 'Home':
                for i in range(4):
                    pixels.append([])
                    pixels[-1].insert(0,'General')
                    if i<2:
                        pixels[-1].append(self.xlsxFile.readCell('E'+str(31+i)))
                        pixels[-1].append(self.xlsxFile.readCell('D'+str(31+i)))
                        pixels[-1].append(self.xlsxFile.readCell('G'+str(31+i)))
                        pixels[-1].append(self.xlsxFile.readCell('F'+str(31+i)))
                        
                        pixels[-1].append(self.xlsxFile.readCell('I'+str(31+i)))
                        pixels[-1].append(self.xlsxFile.readCell('J'+str(31+i)))
                        pixels[-1].append(self.xlsxFile.readCell('K'+str(31+i)))
                        pixels[-1].append(self.xlsxFile.readCell('L'+str(31+i)))
                        pixels[-1].append(self.xlsxFile.readCell('N'+str(31+i)))
                        pixels[-1].append(self.xlsxFile.readCell('O'+str(31+i)))
                    else:
                        pixels[-1].append(self.xlsxFile.readCell('E'+str(31+i+1)))
                        pixels[-1].append(self.xlsxFile.readCell('D'+str(31+i+1)))
                        pixels[-1].append(self.xlsxFile.readCell('G'+str(31+i+1)))
                        pixels[-1].append(self.xlsxFile.readCell('F'+str(31+i+1)))
                        
                        pixels[-1].append(self.xlsxFile.readCell('I'+str(31+i+1)))
                        pixels[-1].append(self.xlsxFile.readCell('J'+str(31+i+1)))
                        pixels[-1].append(self.xlsxFile.readCell('K'+str(31+i+1)))
                        pixels[-1].append(self.xlsxFile.readCell('L'+str(31+i+1)))
                        pixels[-1].append(self.xlsxFile.readCell('N'+str(31+i+1)))
                        pixels[-1].append(self.xlsxFile.readCell('O'+str(31+i+1)))
            else:
                pixels.append([])
                pixels[-1].insert(0, sheetname)
                pixels[-1].append(self.xlsxFile.readCell('E31'))
                pixels[-1].append(self.xlsxFile.readCell('D31'))
                pixels[-1].append(self.xlsxFile.readCell('G31'))
                path_ = urlparse(self.xlsxFile.readCell('F31')).path.split('/')
                self.webDOM.deleteItemList(path_, '')
                self.webDOM.deleteSubPaths(path_)
                try:
                    pixels[-1].append('/'+path_[0])
                except:
                    pixels[-1].append(None)
                pixels[-1].append(self.xlsxFile.readCell('I31'))
                pixels[-1].append(self.xlsxFile.readCell('J31'))
                pixels[-1].append(self.xlsxFile.readCell('K31'))
                pixels[-1].append(self.xlsxFile.readCell('L31'))
                pixels[-1].append(self.xlsxFile.readCell('N31'))
                pixels[-1].append(self.xlsxFile.readCell('O31'))         
        #print(pixels)
        for pixel in pixels:
            print(pixel[4])
        return pixels
    
    def save(self):
        if self.validAdvertiserID() and self.validGTMID():
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
            self.xlsxFile.writeCell('C32', 'Section')
            self.xlsxFile.writeCell('D32', 'Page View')
            self.xlsxFile.writeCell('F32', 'AllPages')
            self.xlsxFile.writeCell('G32', 'u/p')
            self.xlsxFile.writeCell('E32', self.xlsxFile.getNameSection(self.advertiser.get(), 'AllPages','PV'))
            self.xlsxFile.writeCell('C34', 'Section')
            self.xlsxFile.writeCell('D34', 'Scroll')
            self.xlsxFile.writeCell('F34', 'AllPages')
            self.xlsxFile.writeCell('G34', 'u/p')
            self.xlsxFile.writeCell('E34', self.xlsxFile.getNameSection(self.advertiser.get(), 'AllPages','Scroll50'))
            self.xlsxFile.writeCell('C35', 'Section')
            self.xlsxFile.writeCell('D35', 'Timer')
            self.xlsxFile.writeCell('F35', 'AllPages')
            self.xlsxFile.writeCell('G35', 'u/p')
            self.xlsxFile.writeCell('E35', self.xlsxFile.getNameSection(self.advertiser.get(), 'AllPages','T30ss'))
            self.loadData(self.webDOM.arraySections)
            self.xlsxFile.book.remove(self.xlsxFile.book['Sections'])
            directory = filedialog.askdirectory()
            if len(directory) > 0:
                self.directoryTR.set(self.xlsxFile.saveBook(directory))
            else:
                self.directoryTR.set(self.xlsxFile.saveBook())
                #self.xlsxFile.saveBook()
            self.advertiser_.set(self.advertiser.get())
            self.btn_save.configure(state='active')
            self.lanchPopUps('Save', 'The TagCalc file has saved!', 'Press "Ok" to exit.')
        else:
            self.lanchPopUps('Fields missing!', 'Check the Container ID and Advertiser ID!', 'Press "Ok" to exit.')
            
    def savePixels(self):
        self.btn_save_pixels.configure(state='disable')
        snippet_Arrays = {'Xandr Seg': self.xandrSeg, 'Xandr Conv': self.xandrConv, 'DV360': self.DV360, 'Minsights': self.minsights, 'Taboola Seg': self.taboolaSeg, 'Taboola Conv': self.taboolaConv}
        try:
            for DSP in snippet_Arrays:
                index = 0
                for snippet in snippet_Arrays[DSP]:
                    if index == 0 or index == 1 or index == 2 or index == 3:
                        self.xlsxFile.setSheet('Home')
                        if DSP == 'Xandr Seg': 
                            cell = 'J3%s'%str(index+1) if index<2 else 'J3%s'%str(index+2)
                            self.xlsxFile.writeCell(cell, snippet)
                        elif DSP == 'Xandr Conv': 
                            cell = 'K3%s'%str(index+1) if index<2 else 'K3%s'%str(index+2)
                            self.xlsxFile.writeCell(cell, snippet)
                        elif DSP == 'DV360': 
                            cell = 'L3%s'%str(index+1) if index<2 else 'L3%s'%str(index+2)
                            self.xlsxFile.writeCell(cell, snippet)
                        elif DSP == 'Minsights': 
                            cell = 'I3%s'%str(index+1) if index<2 else 'I3%s'%str(index+2)
                            self.xlsxFile.writeCell(cell, snippet)
                        elif DSP == 'Taboola Seg': 
                            cell = 'N3%s'%str(index+1) if index<2 else 'N3%s'%str(index+2)
                            self.xlsxFile.writeCell(cell, snippet)
                        else: 
                            cell = 'O3%s'%str(index+1) if index<2 else 'O3%s'%str(index+2)
                            self.xlsxFile.writeCell(cell, snippet)
                    else:
                        self.xlsxFile.setSheet(self.xlsxFile.book.sheetnames[index-1])
                        if DSP == 'Xandr Seg': 
                            self.xlsxFile.writeCell('J31', snippet)
                        elif DSP == 'Xandr Conv': 
                            self.xlsxFile.writeCell('K31', snippet)
                        elif DSP == 'DV360': 
                            self.xlsxFile.writeCell('L31', snippet)
                        elif DSP == 'Minsights': 
                            self.xlsxFile.writeCell('I31', snippet)
                        elif DSP == 'Taboola Seg': 
                            self.xlsxFile.writeCell('N31', snippet)
                        else: 
                            self.xlsxFile.writeCell('O31', snippet)
                    index += 1  
            directory = filedialog.askdirectory()
            if len(directory) > 0:
                self.directoryTR.set(self.xlsxFile.saveBook(directory, False))
                self.lanchPopUps('Save', 'The Tagging Request file has saved!', 'Press "Ok" to exit.')
            else:
                self.lanchPopUps('Save Error', 'You need to choose a directory!', 'Press "Ok" to exit.')
        except PermissionError:
            self.lanchPopUps('Permission Error!', "The file is open or you haven't permissions.", 'Press "Ok" to exit.')
        except:
            self.lanchPopUps('Error!', str(sys.exc_info()[1]), 'Press "Ok" to exit.')
        self.btn_save_pixels.configure(state='active')
      
    def updateProgress_threaded(self):
        thread = Thread(target = self.updateProgress)
        thread.start()

    def updateProgress(self):
        while self.webDOM.viewProgress > 0:
            self.viewProgress.set(self.webDOM.viewProgress)
            time.sleep(1)
        else:
            print('Se ha finalizado este hilo de seguimiento')
            time.sleep(10)
            self.viewProgress.set(0)
        
    def lanchPopUps(self, title_, message_, detail_):
        messagebox.showinfo(
            title   = title_,
            message = message_,
            detail  = detail_
            )

    # Overwrite the setting's method from child class
    def setting(self):
        self.settingWindow()
        
    def exitCalcTag(self):
        self.webDOM.tearDown()
        self.pixelBot.tearDown()
        self.root.quit()
        self.root.destroy()
        exit()
              
if __name__ == '__main__':
    root = tk.Tk()
    tk.Toplevel()
    tagCalc = tagFrontEnd(root)
    tagCalc.mainloop()
