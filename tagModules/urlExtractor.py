from urllib.parse import urlparse
import requests
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.common.exceptions import StaleElementReferenceException


URL           = 'https://www.xaxis.com/'
CONTRIES      = (
    'co', 'cl', 'ar', 'pe'
    )

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
        self.pathToSave    = ''
        self.__indexSearch = 0
        self.stop          = False
        #self.loadPage()
    
    # This function validate if a url has a valid
    # connection to server in the internet
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
        
    def getUrlTarget(self):
        return self.url_target
    
    def resetMainSections(self):
        self.mainSections  = []
        
    def setHeadlessMode(self):
        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.headless = True
        fireFoxOptions.set_preference("general.useragent.override", USER_AGENT)
        fireFoxOptions.page_load_strategy = 'eager'
        return webdriver.Firefox(options = fireFoxOptions)
    
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
    
    # This function receive a url string and optional position where
    # the element wanted to put
    def addSudDomain(self, subDomain, index = None, type_ = None):
        if type_ == None:
            subDomain = urlparse(subDomain)
        if not self.searchURL(subDomain) and self.opt_url(subDomain):
            if index == None:
                self.subDomains.append(subDomain)
            else:
                self.subDomains.insert(index, subDomain)
            
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
        
    def findTagAttributes(self, tag, return_attribute = 'url'):
        if tag == 'sitemapindex':
            try:
                sitemap_urls = []
                sitemaps = self.driver.find_elements(By.TAG_NAME, 'loc')
                for sitemap in sitemaps:
                    print(sitemap.get_attribute('textContent'))
                    if '.xml' in sitemap.get_attribute('textContent'):
                        sitemap_urls.append(sitemap.get_attribute('textContent'))
                    else:
                        self.addSudDomain(sitemap.get_attribute('textContent'))
                if len(sitemap_urls) > 0:
                    for sitemap_url in sitemap_urls:
                        self.loadPage(sitemap_url)
                        self.findTagAttributes(tag)
                    
#                 for sitemap in sitemaps:
#                     #sitemaps_url.append(sitemap.text)
#                     sitemaps_url.append(sitemap.get_attribute('textContent'))
#                     print(sitemap.get_attribute('textContent'))
#                 return sitemaps_url
            except:
                try:
                    self.findTagAttributes(tag)
                except:
                    self.loadPage()
                    self.findTagAttributes(tag)
        elif tag == 'urlset':
            try:
                urls = []
                urls = self.driver.find_elements(By.TAG_NAME, 'loc')
                for url in urls:
                    #self.addSudDomain(sitemap.text)
                    self.addSudDomain(url.get_attribute('textContent'))
                    print(url.get_attribute('textContent'))
            except:
                try:
                    self.findTagAttributes(tag)
                except:
                    self.loadPage()
                    self.findTagAttributes(tag)
        elif tag == 'a':
            try:
                sitemaps_url = []
                urls         = []
                urls         = self.driver.find_elements(By.TAG_NAME, 'a')
                for url in urls:
                    print(url.get_attribute('textContent'))
                    if '.xml' in url.get_attribute('textContent'):
                        sitemaps_url.append(url.get_attribute('textContent'))
                    else:
                        self.addSudDomain(url.get_attribute('textContent'))
                if len(sitemaps_url) > 0:
                    for sitemap in sitemaps_url:
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
        if self.validURL(url):
            exist_url = True
            for siteMap in SITEMAP_PATH:
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
            #Use this else-for to capture the temporal variable? what?
            self.setDriver(url, True if self.driver == None else False)
            if not exist_sitemap:
                # Implement code to other methods to build the sitemap
                # As Apply scraping to Homepage to build sitemap
                self.findAnchors()
                self.getSubDomains()
                self.deeperSubDomains()
                exist_sitemap = True if len(self.subDomains)>0 else False
            else:
                if len(self.subDomains) < 100:
                    self.deeperSubDomains()
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
        try:
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
#                 if not self.searchURL(url):
#                     self.subDomains.append(url)
#                     print(url.geturl())
            elif len(url.netloc) > 0 and not self.searchURL(url, self.domains):
                self.domains.append(url)
                
    def getArrayURLs(self):
        urls = []
        for url in self.subDomains:
            urls.append(url.geturl())
        urls.sort()
        return urls
                    
    def deeperSubDomains(self):
        if len(self.subDomains) > 0:
            while len(self.subDomains) <100 and self.__indexSearch < len(self.subDomains) and self.subDomains[self.__indexSearch].netloc == urlparse(self.url_target).netloc:
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
            
    def getMainSections(self):
        mainSections = []
        for path in self.getPaths():
            listPath = path.split('/')
            self.deleteItemList(listPath, '')
            url = urlparse(self.url_target)
            # Create Posible Sections to the SiteMap
            if len(listPath)>2:
                continue
            elif len(listPath)>1:
                path_ = listPath[0]+'/'+listPath[1]
                if self.valid_category(path_) and path_ not in mainSections:
                    if not self.similarity_basic(mainSections, listPath[0]) and not self.similarity_basic(mainSections, listPath[1]):
                        mainSections.append(path_)
                    elif self.similarity_basic(mainSections, listPath[0]) and not self.similarity_basic(mainSections, listPath[1]):
                        mainSections.append(path_)
            elif len(listPath)>0 and listPath[0] not in mainSections:
                if self.valid_category(listPath[0]):
                    if not self.similarity_basic(mainSections, listPath[0]):
                        mainSections.append(listPath[0])
            else:
                pass           
        # I need to a process to filter or reduce the number of sections
        # for section in mainSections:
        #if len(mainSections)>9: self.debugMainSections(mainSections)
        mainSections.sort(key=len)
        if len(mainSections)>15:
            self.debugMainSections(mainSections)
        mainSections.insert(0, '')
        return mainSections
    
    def valid_category(self, path):
        paths = path.split('/')
        self.deleteItemList(paths, '')
        if len(paths)>1:
            words = paths[1].split('-')
            self.deleteItemList(words,'')
            for w in words:
                if len(w)<4:
                    words.remove(w)
            if paths[1].isdigit():
                return False
            elif len(words)>2:
                return False
        for path_ in paths:
            path_words = path_.split('-')
            self.deleteItemList(path_words, '')
            if len(path_words)>4 or '_' in path_ or '%' in path_:
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
    # contain the any similarity with the words in the path
    def similarity_basic(self, list_, path):
        similarity = False
        path_words = path.split('-')
        self.deleteItemList(path_words, '')
        for word in path_words:
            if len(word)>3:
                similarity, s = self.searchWord(list_, word, None)
                if similarity:
                    return similarity
        return similarity
    
    def debugMainSections(self, mainSections):
        sections = mainSections[:]
        for i in range(len(mainSections)-1, -1, -1):
            section_words = mainSections[i] 
            section_words = section_words.split('/')
            self.deleteItemList(section_words, '')
            if len(section_words)>1 and i>0:
                for j in range(i-1):
                    if section_words[0] in mainSections[j]:
                        mainSections.pop(i)
                        break    

    def getArraySections(self):
        self.arraySections = []
        arraySections = []
        arrayOtros    = []
        mainSections  = self.getMainSections()
        urls          = self.getArrayURLs()
        paths         = self.getPaths()
        self.mainSections = []
        # Create and Fill out each Sections with urls
        # Firts sort of the URLs by exact category
        for section in mainSections[1:]:
            print("Seccion I: "+section)
            self.mainSections.append(section)
            arraySections.append([])
            # Strategy to labeled each section within the array of URLs
            arraySections[-1].insert(0,section)
            flat = 0
            # Examine of urls finding to determine if own to the section or not
            for path, url in zip(paths[1:],urls[1:]):
                deleteUrls = []
                flat += 1
                print(flat)
                path_list = path.split('/')
                self.deleteItemList(path_list, '')
                if len(path_list)>1:
                    path_list_ = path_list[0]+'/'+path_list[1]
                    if path_list_ in section:
                        arraySections[-1].append(url)
                        paths.pop(paths.index(path))
                        urls.pop(urls.index(url))
                        continue
                elif len(path_list)>0 and path_list[0] in section:
                    arraySections[-1].append(url)
                    paths.pop(paths.index(path))
                    urls.pop(urls.index(url))
                    continue
        
        # Second sort of the URLs by similarity category        
        for section, arraySection in zip(mainSections[1:], arraySections):
            print("Seccion II: "+section)
            flat = 0
            # Examine of urls finding to determine if own to the section or not
            for path, url in zip(paths[1:],urls[1:]):
                #deleteUrls = []
                flat += 1
                print(flat)
                path_list = path.split('/')
                self.deleteItemList(path_list, '')
                if len(path_list)>1:
                    if self.similarity_basic([section], path_list[0]) or self.similarity_basic([section], path_list[1]):
                        arraySection.append(url)
                        paths.pop(paths.index(path))
                        urls.pop(urls.index(url))
                        continue
                elif len(path_list)>0:
                    if self.similarity_basic([section], path_list[0]):
                        arraySection.append(url)
                        paths.pop(paths.index(path))
                        urls.pop(urls.index(url))
                        continue
#                 if len(deleteUrls)>0:
#                     paths.pop(paths.index(deleteUrls[-1][0]))
#                     urls.pop(urls.index(deleteUrls[-1][1]))
        
        arraySections.sort(key=len, reverse=True)
        for i in range(len(arraySections)):
            self.mainSections[i] = arraySections[i][0]
            arraySections[i].pop(0)
        
        #arraySections.sort(reverse=True, key=len)
        if len(urls)>1:
            self.mainSections.append('Otros')
            arraySections.append(urls[1:])
           
        if len(arraySections)>20:
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
    webSite = urlDomains('https://www.stevemaddenperu.com/')
#     webSite.driver = webSite.setHeadlessMode()
#     webSite.loadPage()
#     webSite.findAnchors()
#     webSite.getSubDomains()
#     for path in webSite.getPaths():
#         print(path)
#     webSite.deeperSubDomains()
#     sections = webSite.getArraySections() 
    
