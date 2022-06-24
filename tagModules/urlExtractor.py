from urllib.parse import urlparse
import requests
import time

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By

from selenium.common.exceptions import StaleElementReferenceException


URL           = 'https://www.xaxis.com/'

SITEMAP_PATH  = (
    'sitemap.xml', '1_index_sitemap.xml', 'sitemap-index.html', 'sitemap_index.xml', 'sitemap'
    )

DISALLOW_PATH = (
    '.pdf', '.xml', 'xlsx', 'xls', '.jpg',')', '1048x1080', '462x664', '1920x1080', '640x1000', 'icone', 'icon'
    )

USER_AGENT    = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'

HEADERS       = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    }

class urlDomains:
    def __init__(self, url_target = URL):
        self.url_target    = url_target
        self.driver        = None
        self.anchors       = []
        self.allDomains    = []
        self.subDomains    = []
        self.domains       = []
        self.mainSections  = []
        self.arraySections = []
        self.urlsets       = []
        self.searchXML     = True
        self.maxLandings   = 50
        self.sizeWord      = 3
        self.maxCategories = 15
        self.landingsBy    = 2
        self.pathToSave    = ''
        self.__indexSearch = 0
        self.stop          = False
        self.thirdSubPath  = False
        self.viewProgress  = 0
        #self.loadPage()
    
    # This function validate if a url has a valid connection to server in the internet
    # Receive a string url
    def validURL(self, url):
        try:
            if requests.get(url, headers = HEADERS).status_code == 200:
                return True
            else:
                return False
        except:
            return False
    
    def validRootDomain(self):
        pass
    
    def setUrlTarget(self, url):
        self.url_target = url

    def setSearchXML(self, searchXML):
        self.searchXML = searchXML

    def setMaxLandings(self, maxLandings):
        self.maxLandings = maxLandings

    def setMaxCategories(self, maxCategories):
        self.maxCategories = maxCategories

    def setSizeWord(self, sizeWord):
        self.sizeWord = sizeWord
        
    def setLandingsBy(self, landings):
        self.landingsBy = landings

    def setStop(self, stop):
        self.stop = stop
        
    def getUrlTarget(self):
        return self.url_target

    def getSearchXML(self):
        return self.searchXML

    def getMaxLandings(self):
        return self.maxLandings
    
    def resetMainSections(self):
        self.mainSections  = []
        
    def setHeadlessMode(self):
        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.headless = True
        fireFoxOptions.set_preference("general.useragent.override", USER_AGENT)
        #fireFoxOptions.page_load_strategy = 'eager'
        service = FirefoxService(executable_path=GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options = fireFoxOptions)
    
    def loadPage(self, url = None):
        if url == None:
            url = self.url_target
        self.driver.get(url)
        
    # This method receive urlparse type  element and optional array of urlparse type elements.
    # If the array is not passed, then the url is searched in the attribute subDomains.
    # Return True if the url is founded in the array and False in other case.
    def searchURL(self, url, arrayDomains = None):
        if arrayDomains == None:
            arrayDomains = self.subDomains
        for domain in arrayDomains:
            if url.geturl() == domain.geturl():
                return True
        return False
    
    # This method receive a URL parameter and determine if the landing owns to right page
    # or this URL redirect to type file type as pdf, excel, image or other type of file.
    def opt_url(self, url, type_ = None):
        if type_ == None:
            url_ = url
        else:
            url_ = urlparse(url)
        if urlparse(self.url_target).netloc != url_.netloc or url_.scheme != 'https':
            return False
        for DP in DISALLOW_PATH:
            if DP in url_.path:
                return False
        else:
            return True
    
    # This function receive a url string and optional parameter if it's necesary to parse URL 
    # If this URL isn't in the URLs founded until the moment and it's a valid URL then it's added
    def addSudDomain(self, subDomain, index = None, type_ = None):
        if type_ == None:
            subDomain = urlparse(subDomain)
        if not self.searchURL(subDomain) and self.opt_url(subDomain):
            if index == None:
                self.subDomains.append(subDomain)
            else:
                self.subDomains.insert(index, subDomain)

    # Delete all URL or one URL  from the array of URLs founded in the website        
    def deleteSubDomain(self, index = None):
        if index == None:
            self.subDomains.pop()
        elif index == 'All':
            self.subDomains.clear()
        else:
            self.subDomains.pop(index)
            
    def setDriver(self, url, setDriver = False):
        if setDriver:
            self.driver = self.setHeadlessMode()
        self.setUrlTarget(url)
        self.loadPage()
    
    def existGTM(self, url):
        GTMs = []
        GTM_ID = 'GTM-XXXXXXX'
        self.setDriver(url)
        time.sleep(10)
        GTMs = self.driver.find_elements(By.XPATH,'//script[contains(text(),"(function(w,d,s,l,i)") or contains(text(),"googletagmanager")]')
        if len(GTMs)>0:
            IDs = self.driver.find_elements(By.XPATH,'//script[contains(@src,"googletagmanager") and contains(@src,"GTM")]')
            for ID in IDs:
                ID = urlparse(ID.get_attribute('src'))
                for GTM in GTMs:
                    if ID.query[3:] in GTM.get_attribute('textContent'):
                        return True, ID.query[3:]
            else:
                for GTM in GTMs:
                    if 'GTM-' in GTM.get_attribute('textContent'):
                        try:
                            GTM_ID = GTM.get_attribute('textContent')[GTM.get_attribute('textContent').find('GTM-'):GTM.get_attribute('textContent').find('GTM-')+11]
                        except:
                            pass
                        return True, GTM_ID
                else:
                    return True, GTM_ID
        else:
            return False, GTM_ID
        
    def findTagAttributes(self, tag, return_attribute = 'url'):
        if tag == 'sitemapindex' and not self.stop:
            try: 
                sitemap_urls = []
                sitemaps = self.driver.find_elements(By.TAG_NAME, 'loc')
                for sitemap in sitemaps:
                    if self.stop: break
                    print(sitemap.get_attribute('textContent'))
                    if '.xml' in sitemap.get_attribute('textContent'):
                        sitemap_urls.append(sitemap.get_attribute('textContent'))
                    else:
                        self.addSudDomain(sitemap.get_attribute('textContent'))
                if len(sitemap_urls) > 0:
                    for sitemap_url in sitemap_urls:
                        if self.stop: break
                        self.loadPage(sitemap_url)
                        self.findTagAttributes(tag)
            except:
                try:
                    self.findTagAttributes(tag)
                except:
                    self.loadPage()
                    self.findTagAttributes(tag)
        elif tag == 'urlset' and not self.stop:
            try:
                urls = []
                urls = self.driver.find_elements(By.TAG_NAME, 'loc')
                for url in urls:
                    #self.addSudDomain(sitemap.text)
                    if self.stop: break
                    self.addSudDomain(url.get_attribute('textContent'))
                    print(url.get_attribute('textContent'))
            except:
                try:
                    self.findTagAttributes(tag)
                except:
                    self.loadPage()
                    self.findTagAttributes(tag)
        elif tag == 'a' and not self.stop:
            try:
                sitemaps_url = []
                urls         = []
                urls         = self.driver.find_elements(By.TAG_NAME, 'a')
                for url in urls:
                    print(url.get_attribute('textContent'))
                    if self.stop: break
                    if '.xml' in url.get_attribute('textContent'):
                        sitemaps_url.append(url.get_attribute('textContent'))
                    else:
                        self.addSudDomain(url.get_attribute('textContent'))
                if len(sitemaps_url) > 0:
                    for sitemap in sitemaps_url:
                        if self.stop: break
                        self.setUrlTarget(sitemap)
                        self.loadPage()
                        self.findTagAttributes(tag)
            except:
                try:
                    self.findTagAttributes(tag)
                except:
                    self.loadPage()
                    self.findTagAttributes(tag)
    
    def buildSiteMap(self, url):
        self.deleteSubDomain('All')
        exist_url     = False
        exist_sitemap = False
        self.viewProgress = 2
        if self.validURL(url):
            exist_url = True
            if self.searchXML:
                for siteMap in SITEMAP_PATH:
                    if self.stop:
                        break
                    # Try to connect to the generic sitemap url, as: domain.com/sitemap.xml
                    url_sitemap = urlparse(url)._replace(path=siteMap, params='',query='',fragment='').geturl()
                    if self.validURL(url_sitemap):
                        self.setDriver(url_sitemap, True if self.driver == None else False)
                        xml_title, w = self.searchWord(self.driver.title, 'xml', paragraph=True)
                        print('Ha cargado el emulador')
                        # In this level we need to validate and implement solution to differents
                        # sitemap format even to the sitemap that it's no exist.
                        if self.validTag(self.driver, 'sitemapindex'):
                            self.findTagAttributes('sitemapindex')
                            exist_sitemap = True if len(self.subDomains)>0 else False
                            break
                        elif self.validTag(self.driver, 'urlset'):
                            self.findTagAttributes('urlset')
                            exist_sitemap = True if len(self.subDomains)>0 else False
                            break
                        #elif: Continue implement other formats the sitemap
                        elif xml_title:
                            print("With get in by Web Title")
                            self.findTagAttributes('a')
                            exist_sitemap = True if len(self.subDomains)>0 else False
                            break   
            self.viewProgress = 20              
            self.setDriver(url, True if self.driver == None else False)
            self.viewProgress = 30
            self.findAnchors()
            self.viewProgress = 40
            self.getSubDomains()
            self.viewProgress = 50
            self.deeperSubDomains()
            self.viewProgress = 99
            exist_sitemap = True if len(self.subDomains)>0 else False
            print('Hemos terminado la validación')
            return exist_url, exist_sitemap
        else:
            # Return False if the url is invalid 
            return exist_url, exist_sitemap
        
    def validTag(self, browser, tag_name):
        try:
            browser.find_element(By.TAG_NAME, tag_name)
            return True
        except:
            return False
        
    # This fuction find all urls in a webpage, scraping all anchor elements in the webpage
    # This function stores urls that owns or not to the main domain as urlparse type
    def findAnchors(self):
        flat = 0
        try:
            self.anchors = self.driver.find_elements(By.TAG_NAME, 'a')
            while flat<3:
                if len(self.anchors)>1:
                    flat = 3
                else:
                    time.sleep(15)
                    self.anchors = self.driver.find_elements(By.TAG_NAME, 'a')
            for anchor in self.anchors:
                self.allDomains.append(urlparse(anchor.get_attribute('href')))
        except:
            try:
                self.allDomains = []
                self.findAnchors()
            except:
                self.allDomains = []
                self.loadPage()
                self.findAnchors()      
    
    # This function sort of all urls founded in the webpage in two categories:
    # SubDomains: domains that own to the main domain given
    # Domains: domains that not own to the main domain given
    def getSubDomains(self):
        for url in self.allDomains:
            if urlparse(self.url_target).netloc == url.netloc:
                self.addSudDomain(url, type_ = 1)
            elif len(url.netloc) > 0 and not self.searchURL(url, self.domains):
                self.domains.append(url)
            if self.stop:
                break
                
    def getArrayURLs(self):
        urls = []
        for url in self.subDomains:
            urls.append(url.geturl())
        urls.sort()
        return urls
                    
    def deeperSubDomains(self):
        if len(self.subDomains) > 0:
            while len(self.subDomains)<self.maxLandings and self.__indexSearch<len(self.subDomains) and self.subDomains[self.__indexSearch].netloc == urlparse(self.url_target).netloc and not self.stop:
                try:
                    self.loadPage(self.subDomains[self.__indexSearch].geturl())
                    self.findAnchors()
                    self.getSubDomains()
                    self.__indexSearch += 1
                except StaleElementReferenceException as e:
                    print('Ha ocurrido un error')
                    try:
                        self.driver.refresh()
                        self.findAnchors()
                        self.getSubDomains()
                        self.__indexSearch += 1
                    except StaleElementReferenceException as e:
                        self.__indexSearch += 1
                print('Index URL/Total: '+ str(self.__indexSearch) + '/' + str(len(self.subDomains)))
            print("Hemos Terminado")
            self.__indexSearch = 0
        else:
            print('No hay Dominios Principales')
    # This function return a array of paths with the character /        
    def getPaths(self):
        paths = []
        for subDomain in self.subDomains:
            paths.append(subDomain.path)
        paths.sort()
        return paths
    
    # Function to delete a item from a list_ by value
    def deleteItemList(self, list_, item):
        for i in range(list_.count(item)):
            list_.pop(list_.index(item))
    
    # This method creates all sections under that we can organize the landings founded       
    def getMainSections_(self):
        mainSections = []
        for path in self.getPaths():
            path     = path.replace('.html','') 
            listPath = path.split('/')
            self.deleteItemList(listPath, '')
            # Create Posible Sections to the SiteMap
            if len(listPath)>3:
                continue
            elif len(listPath)>2 and self.thirdSubPath and listPath[2] not in mainSections:
                if self.valid_category(listPath[2]):
                    path_ = listPath[0]+'/'+listPath[1]+'/'+listPath[2]
                    mainSections.append(path_)
            elif len(listPath)>1 and not self.thirdSubPath:
                path_ = listPath[0]+'/'+listPath[1]
                if self.valid_category(path_) and path_ not in mainSections:
                    if not self.similarity_basic(mainSections, listPath[0]) and not self.similarity_basic(mainSections, listPath[1]):
                        mainSections.append(path_)
                    elif not self.similarity_basic(mainSections, listPath[0]):
                        mainSections.append(path_)
            elif len(listPath)>0 and listPath[0] not in mainSections and not self.thirdSubPath:
                if self.valid_category(listPath[0]):
                    mainSections.append(listPath[0])
                    #if not self.similarity_basic(mainSections, listPath[0]):
                        #mainSections.append(listPath[0])
            else:
                pass           
        # I need to a process to filter or reduce the number of sections
        # for section in mainSections:
        #if len(mainSections)>9: self.debugMainSections(mainSections)
        if len(mainSections)<2:
            print('Hemos entrado a Third Path Categorize')
            self.thirdSubPath = True
            for newSection in self.getMainSections():
                mainSections.append(newSection)
            self.thirdSubPath = False
        mainSections.sort(key=len)
        if len(mainSections)>self.maxCategories:
            self.debugMainSections(mainSections)
        if not mainSections[0]=='':
            mainSections.insert(0, '')
        return mainSections
    
    def getMainSections(self):
        mainSections = []
        for path in self.getPaths():
            path     = path.replace('.html','') 
            path     = path.replace('.php','')
            listPath = path.split('/')
            self.deleteItemList(listPath, '')
            self.deleteSubPaths(listPath)
            if len(listPath)>2:
                continue
            elif len(listPath)>1:
                path_ = listPath[0]+'/'+listPath[1]
                if self.valid_category(path_) and path_ not in mainSections and not self.similaritySubPath(mainSections, listPath[0]):
                    mainSections.append(path_)
                    # if not self.similarity_basic(mainSections, listPath[0]) and not self.similarity_basic(mainSections, listPath[1]):
                    #     mainSections.append(path_)
                    # elif not self.similarity_basic(mainSections, listPath[0]):
                    #     mainSections.append(path_)
            elif len(listPath)>0 and listPath[0] not in mainSections:
                if self.valid_category(listPath[0]):
                    mainSections.append(listPath[0])
            else:
                pass           
        mainSections.sort(key=len)
        #if len(mainSections)>self.maxCategories:
            #self.debugMainSections(mainSections)
        if not mainSections[0]=='':
            mainSections.insert(0, '')
        return mainSections
    
    def deleteSubPaths(self, subPaths, size_=3):
        for subPath in subPaths:
            if len(subPath)<size_:
                subPaths.pop(subPaths.index(subPath))
            elif subPath.replace('-','').isnumeric():
                subPaths.pop(subPaths.index(subPath))
                
    """This function implement the search of exact coincidence by subpath.
        Parameters:
            list_paths:     Array list of paths.add()
            subPath:        Subpath that we want to know if exist in the array list paths.
            numSubPath:     Position of the subPath in the Paths.
        Return:
            Boolean:        True if the subpath exists in the array list of the paths.
    """
    def similaritySubPath(self, list_paths, subPath, numSubpath=0):
        try: 
            for path in list_paths:
                path = path.split('/')
                self.deleteItemList(path, '')
                if numSubpath == 0:
                    if len(path)>0:
                        if path[0].casefold() == subPath.casefold():
                            return True
                elif numSubpath == 1:
                    if len(path)>1:
                        if path[1].casefold() == subPath.casefold():
                            return True
                elif numSubpath == 2:
                    if len(path)>2:
                        if path[2].casefold() == subPath.casefold():
                            return True
                else:
                    continue
            else:
                return False
        except:
            return False
                
    # Determine if a path is valid to be a candidate to be a section
    def valid_category(self, path):
        path  = path.replace('.html','')
        paths = path.split('/')
        self.deleteItemList(paths, '')
        if len(paths)>1:
            words = []
            for subPath in paths:
                words.append(subPath.split('-'))
                self.deleteItemList(words[-1],'')
                for word in words[-1]:
                    if len(word)<self.sizeWord:
                        words[-1].remove(word)
            if paths[1].isdigit() or len(words[0])>3 or len(words[1])>3 or '%' in subPath:#We had changed the len(words[0/1])>2 to len(words)>3
                return False
            elif len(words[0])<1 and len(words[1])<1:
                return False
            elif paths[0].isdigit() and paths[1].isdigit():
                return False
            else:
                print(words)
                return True 
        elif len(paths)>0:
            words = paths[0].split('-')
            self.deleteItemList(words,'')
            for word in words:
                if len(word)<self.sizeWord:
                    words.remove(word)
            if paths[0].isdigit() or len(words)>3 or len(words)==0 or '_' in paths[0] or '%' in paths[0]:#We had changed the len(words)>2 to len(words)>3
                return False
            else:
                return True

    # This function allows to search a word in paragraph or a list_
    # If paragraph parameter is True, then list_ will be a string paragraph
    # If it's False, then list will be a list of words
    # Return True if the word is founded and the next word to it.
    def searchWord(self, list_, word, delimeter=' ', paragraph = False):
        if paragraph:
            list_ = list_.casefold()
            word = word.casefold()
            split_text = list_.split(delimeter)
            if word in split_text:
                if (split_text.index(word)+1) < len(split_text):
                    return True, split_text[split_text.index(word)+1]
                else:
                    return True, -1
            else:
                return False, None
        else:
            for item in list_:
                if word.casefold() in item.casefold():
                    return True, None
            else:
                return False, None
            
    # This function receive a list_ where finding if it 
    # contain the any similarity with the words in the subpath
    def similarity_basic(self, list_, subpath, size_word = 2):
        similarity = False
        subpath_words = subpath.split('-')
        self.deleteItemList(subpath_words, '')
        for word in subpath_words:
            if len(word)>size_word:
                similarity, s = self.searchWord(list_, word, None)
                if similarity:
                    return similarity
        return similarity
    
    def debugMainSections(self, mainSections):
        sections = mainSections[:]
        for i in range(len(mainSections)-1, -1, -1):
            path_words = []
            section_words = mainSections[i] 
            section_words = section_words.split('/')
            self.deleteItemList(section_words, '')
            for section_word in section_words:
                section_word = section_word.split('-')
                self.deleteItemList(section_word, '')
                # Doing the test with len(word)>4 and 3
                for word in section_word:
                    if len(word)>self.sizeWord:
                        path_words.append(word)
            if i>0:
                print(path_words)
                print(i)
                for word in path_words:
                    exist, h = self.searchWord(sections[:i], word, None)
                    #exist1, h = self.searchWord(sections[:i], word[:-1], None)
                    if exist:
                        print('Delete Section:  '+ mainSections[i])
                        mainSections.pop(i)
                        break
                    
    def filterMainSections(self, mainSections):
        sections = mainSections[:]
        for i in range(len(mainSections)-1, -1, -1):
            section_words = mainSections[i].split('/')
            self.deleteItemList(section_words, '')
            if len(section_words)>1:
                pass

    # Dumping in the differents sections of the landings founded in the website
    def getArraySections_(self):
        self.arraySections = []
        self.mainSections  = []
        arraySections      = []
        mainSections  = self.getMainSections()
        urls          = self.getArrayURLs()
        paths         = self.getPaths()
        
        # Create and Fill out each Sections with urls
        # Firts sort of the URLs by exact category
        for section in mainSections[1:]:
            print("Seccion I: "+section)
            self.mainSections.append(section)
            arraySections.append([])
            # Strategy to labeled each section within the array of URLs
            arraySections[-1].insert(0,section)
            flat = 0
            section_ = section.split('/')
            self.deleteItemList(section_, '')
            # Examine of urls finding to determine if own to the section or not
            for path, url in zip(paths[1:],urls[1:]):
                flat += 1
                print(flat)
                path_list = path.split('/')
                self.deleteItemList(path_list, '')
                if len(path_list)>1:
                    path_list_ = path_list[0]+'/'+path_list[1]
                    if path_list_ in section or section in path_list:
                        arraySections[-1].append(url)
                        paths.pop(paths.index(path))
                        urls.pop(urls.index(url))
                        continue
                    elif path_list[0] == section_[0]:
                        arraySections[-1].append(url)
                        paths.pop(paths.index(path))
                        urls.pop(urls.index(url))
                        continue
                elif len(path_list)>0 and path_list[0] in section:
                    arraySections[-1].append(url)
                    paths.pop(paths.index(path))
                    urls.pop(urls.index(url))
                    continue
        #Second sort of the URLs by similarity category 
        for section, arraySection in zip(mainSections[1:], arraySections):
            print("Seccion II: "+section)
            flat = 0
            # Examine of urls finding to determine if own to the section or not
            for path, url in zip(paths[1:],urls[1:]):
                flat += 1
                print(flat)
                path_list = path.split('/')
                self.deleteItemList(path_list, '')
                if len(path_list)>1:
                    if self.similarity_basic([section], path_list[0],4) or self.similarity_basic([section], path_list[1],4):
                        arraySection.append(url)
                        paths.pop(paths.index(path))
                        urls.pop(urls.index(url))
                        continue
                elif len(path_list)>0:
                    if self.similarity_basic([section], path_list[0],4):
                        arraySection.append(url)
                        paths.pop(paths.index(path))
                        urls.pop(urls.index(url))
                        continue  
        
        #Process to sort of the most dominants categories by number of landings
        arraySections.sort(key=len, reverse=True)
        for i in range(len(arraySections)):
            self.mainSections[i] = arraySections[i][0]
            arraySections[i].pop(0)
        
        #arraySections.sort(reverse=True, key=len)
        if len(urls)>1:
            self.mainSections.append('Otros')
            arraySections.append(urls[1:])
           
        if len(arraySections)>self.maxCategories:
            for i, j in zip(range(len(arraySections)-1, -1, -1), range(len(self.mainSections)-1, -1, -1)):
                if len(arraySections[i]) > 2:
                    continue
                elif len(arraySections[i]) > 1:
                    print('Delete Section: '+ self.mainSections[j]+'  With index: '+str(j))
                    self.mainSections.pop(j)
                    arraySections[-1].insert(0, arraySections[i][0])
                    arraySections[-1].insert(0, arraySections[i][1])
                    arraySections.pop(i)
                elif len(arraySections[i]) > 0:
                    print('Delete Section: '+ self.mainSections[j]+'  With index: '+str(j))
                    self.mainSections.pop(j)
                    arraySections[-1].append(arraySections[i][0])
                    arraySections.pop(i)
        for i in range(len(arraySections)):
            arraySections[i].sort()
        self.mainSections.insert(0,'') 
        self.arraySections = arraySections
        #return arraySections
        
    def getArraySections(self):
        self.arraySections = []
        self.mainSections  = []
        arraySections      = []
        mainSections  = self.getMainSections()
        urls          = self.getArrayURLs()
        paths         = self.getPaths()
        
        # Create and Fill out each Sections with urls
        # Firts sort of the URLs by exact category
        for section in mainSections[1:]:
            print("Seccion I: "+section)
            self.mainSections.append(section)
            arraySections.append([])
            # Strategy to labeled each section within the array of URLs
            arraySections[-1].insert(0,section)
            flat = 0
            section_ = section.split('/')
            self.deleteItemList(section_, '')
            # Examine of urls finding to determine if own to the section or not
            for path, url in zip(paths[1:],urls[1:]):
                path_ = path.replace('.html','')
                path_ = path.replace('.php','')
                subpaths = path_.split('/')
                self.deleteItemList(subpaths, '')
                self.deleteSubPaths(subpaths)
                if len(subpaths)>1:
                    mainSubPath = subpaths[0]+'/'+subpaths[1]
                    if mainSubPath in section:
                        arraySections[-1].append(url)
                        paths.pop(paths.index(path))
                        urls.pop(urls.index(url))
                        continue
                    elif subpaths[0] == section_[0]:
                        arraySections[-1].append(url)
                        paths.pop(paths.index(path))
                        urls.pop(urls.index(url))
                        continue
                elif len(subpaths)>0 and subpaths[0] == section_[0]:
                    arraySections[-1].append(url)
                    paths.pop(paths.index(path))
                    urls.pop(urls.index(url))
                    continue
        if len(paths)>1:
            for path,url in zip(paths[1:],urls[1:]):
                newCategory = []
                path_ = path.replace('.html','')
                path_ = path.replace('.php','')
                subpaths = path_.split('/')
                self.deleteItemList(subpaths, '')
                self.deleteSubPaths(subpaths)
                try:
                    for p,u in zip(paths[paths.index(path)+1:],urls[paths.index(path)+1:]):
                        p_ = p.replace('.html','')
                        p_ = p.replace('.php','')
                        subPs = p_.split('/')
                        self.deleteItemList(subPs, '')
                        self.deleteSubPaths(subPs)
                        if len(subPs)>0 and len(subpaths)>0 and subPs[0] == subpaths[0]:
                            newCategory.append(u)
                            paths.pop(paths.index(p))
                            urls.pop(urls.index(u))
                except:
                    pass
                if len(newCategory)>0:
                    self.mainSections.append(subpaths[0])
                    arraySections.append([])
                    arraySections[-1].insert(0,subpaths[0])
                    paths.pop(paths.index(path))
                    urls.pop(urls.index(url))
                    for url_ in newCategory:
                        arraySections[-1].append(url_)
                        
        #Process to sort of the most dominants categories by number of landings
        arraySections.sort(key=len, reverse=True)
        # for i in range(len(arraySections)):
        #     self.mainSections[i] = arraySections[i][0]
        #     arraySections[i].pop(0)
        for i in range(len(arraySections)-1,-1,-1):
            if len(arraySections[i])>self.landingsBy:
                self.mainSections[i] = arraySections[i][0]
                arraySections[i].pop(0)
            else:
                for landing in arraySections[i][:]:
                    urls.append(landing)
                arraySections.pop(i)
                self.mainSections.pop(i)
        #arraySections.sort(reverse=True, key=len)     
        for arraySection, mainSection in zip(arraySections,self.mainSections):
            if len(arraySection) == 0:
                arraySections.remove(arraySection)
                self.mainSections.remove(mainSection)
           
        if len(arraySections)>self.maxCategories:
            for i, j in zip(range(len(arraySections)-1, -1, -1), range(len(self.mainSections)-1, -1, -1)):
                if len(arraySections[i]) > 2:
                    continue
                elif len(arraySections[i]) > 1:
                    print('Delete Section: '+ self.mainSections[j]+'  With index: '+str(j))
                    self.mainSections.pop(j)
                    urls.append(arraySections[i][0])
                    urls.append(arraySections[i][1])
                    #arraySections[-1].insert(0, arraySections[i][0])
                    #arraySections[-1].insert(0, arraySections[i][1])
                    arraySections.pop(i)
                elif len(arraySections[i]) > 0:
                    print('Delete Section: '+ self.mainSections[j]+'  With index: '+str(j))
                    self.mainSections.pop(j)
                    urls.append(arraySections[i][0])
                    #arraySections[-1].append(arraySections[i][0])
                    arraySections.pop(i)
                elif len(arraySections[i]) == 0:
                    self.mainSections.pop(j)
                    arraySections.pop(i)
                if len(arraySections)<self.maxCategories+1:
                    break
        
        if len(urls)>1:
            self.mainSections.append('Otros')
            arraySections.append(urls[1:])
            
        for i in range(len(arraySections)):
            arraySections[i].sort()
        self.mainSections.insert(0,'') 
        self.arraySections = arraySections
        #return arraySections
    
    def getArraySectionsII(self):
        arraySections = []
        self.mainSections = []
        self.mainSections.insert(0,'')
        self.mainSections.insert(1,'Landings')
        urls = self.getArrayURLs()
        arraySections.append(urls)
        self.arraySections = arraySections
        #return arraySections
    
    def getParams(self):
        params = []
        for subDomain in self.subDomains:
            params.append(self.subDomains.params)
        return params

    def tearDown(self):
        if not self.driver == None:
            self.driver.quit()
    

if __name__ == '__main__':
#     write test code module
    webSite = urlDomains('https://compra.tusegurometlife.cl/')
    webSite.driver = webSite.setHeadlessMode()
    webSite.loadPage()
    #webSite.buildSiteMap('https://compra.tusegurometlife.cl/')
##    index = 0
##    for section in webSite.getMainSections():
##        print('Section '+str(index)+':'+'  '+section)
##        index += 1
#     webSite.findAnchors()
#     webSite.getSubDomains()
#     for path in webSite.getPaths():
#         print(path)
#     webSite.deeperSubDomains()
#     sections = webSite.getArraySections() 
