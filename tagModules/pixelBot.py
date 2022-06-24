from urllib.parse import urlparse
import requests
import time, sys
import re

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from selenium.common.exceptions import *

LOGIN      = {
    'sign in', 'acceso: cuentas', 'login', 'log in', 'account', 'iniciar sesión', 'cuenta'
    }

VERIFY     = {
    '2nd factor', 'authentication', 'Check Your Email', 'Verification', 'Verify'
    }

HOME       = {
    'Display & Video 360', 'Home', 'Day - '
    }

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'

PASSWORDS  = {
    'Xandrs': 'xAXIS_2021*!', 'Taboola': 'Xaxis_2021*!', 'DV360': 'Xaxis_2021**'
    }

MARKETS    = {
    'Argentina': '1893', 'Brazil': '1663', 'Chile': '7534','Colombia': '1892', 'Ecuador': '13135', 'Mexico': '1891', 'Miami': '2038', 'Peru': '7348', 'Puerto Rico': '6982', 'Uruguay': '7535'
}

class pixelBot:
    def __init__(self):
        self.driver       = None
        self.url          = None
        self.authFail     = False
        self.set          = True
        self.reqCode      = False
        self.verifyWE     = None
        self.codeWE       = None
        self.emailWE      = None
        self.passwdWE     = None
        self.submitWE     = None
        self.startLog     = False
        self.code         = None
        self.approve      = False
        self.viewProgress = 0

    def setUrl(self, url):
        self.url = url

    def setDriver(self, url):
        if self.set:
            self.driver = self.setHeadlessMode()
            self.set    = False
        self.driver.maximize_window()
        self.setUrl(url)
        self.loadPage()

    def getUrl(self):
        return self.url

    def getDriver(self):
        return self.driver

    def setHeadlessMode(self):
        fireFoxOptions = webdriver.FirefoxOptions()
        #fireFoxOptions.headless = True
        fireFoxOptions.set_preference("general.useragent.override", USER_AGENT)
        #fireFoxOptions.page_load_strategy = 'eager'
        service = FirefoxService(executable_path=GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options = fireFoxOptions)
    
    def loadPage(self, url = None):
        if url == None:
            url = self.url
        self.driver.get(url)
        
    """Function that implement a wait while there is a change in the URL.
       Parameters:
            url:
            timeout:
            kkk
       Return:
            Boolean: True or false if a change is detected in the URL.
    """
    def waitChangeURL(self, url, timeout=60):
        try:
            WebDriverWait(self.driver, timeout).until(EC.url_changes(url))
            return True
        except:
            return False
        
    """Function that detects if there was a change in a webpage or webelement.
        Parameters:
        Return:
            Boolean: True/False if there was a change.
    """
    def waitChange(self, locator, attribute, text, timeout):
        try:
            if WebDriverWait(self.driver, 1).until(EC.text_to_be_present_in_element_attribute(locator, attribute, text)):
                try:
                    while WebDriverWait(self.driver, timeout).until(EC.text_to_be_present_in_element_attribute(locator, attribute, text)): pass
                except:
                    return True
        except:
            return False
        
    """
        This method searches a specific webElement through many iterations....
        Return:
            WebElement, error: WebElement or -1, and error object or None     
    """   
    def getWebElement(self, typeSearch, expression, timeout_=10, max_iteractions=6, visible = True, driver = None):
        flat = 0
        while flat<max_iteractions:
            if typeSearch=='XPATH' and visible:
                try:
                    if driver == None:
                        webElement = WebDriverWait(self.driver, timeout_).until(EC.visibility_of_any_elements_located((By.XPATH, expression)))
                    else:
                        webElement = WebDriverWait(driver, timeout_).until(EC.visibility_of_any_elements_located((By.XPATH, expression)))
                    return webElement, None
                except TimeoutException as e:
                    flat += 1
                    if flat>=max_iteractions:
                        return -1, e
                except InvalidSelectorException as e:
                    return -1, e
                except:
                    return -1, sys.exc_info()
            elif typeSearch=='XPATH' and  not visible:
                try:
                    while flat<max_iteractions:
                        time.sleep(1)
                        if driver == None:
                            webElement = self.driver.find_elements(By.XPATH, expression)
                        else:
                            webElement = driver.find_elements(By.XPATH, expression)
                        if len(webElement)>0:
                            return webElement, None
                        flat += 1
                    else:
                        return -1, None
                except InvalidSelectorException as e:
                    return -1, e
                except:
                    return -1, sys.exc_info()
            elif typeSearch == 'TAG_NAME':
                pass
            elif typeSearch == 'CLASS':
                pass
        return -1, None
        
    
    """ Function that wait certain amount of time while the webelement is enabled.
        Parameters:
            webElement: HTML element that we need to wait to be enabled.
            condition:  Condition that determines if the webElement is enabled or not.
            timeout:
            interactions:
        Return:
            None:   None.
    """
    def waitWebElement(self, webElement, expression, condition='default', timeout=1, interactions=60):
        flat = 0
        code = 200
        if condition == 'default':
            while flat<interactions:
                time.sleep(timeout)
                try:
                    if webElement.get_attribute('disabled') == None or webElement.get_attribute('disabled') == False:
                        return code
                except StaleElementReferenceException:
                    code = 404
                    element, elementError = self.getWebElement('XPATH', expression)
                    if element != -1: webElement = element[0] 
                flat += 1
        elif condition == 'class':
            while flat<interactions:
                time.sleep(timeout)
                if 'disabled' in webElement.get_attribute('class'):
                    flat += 1
                else:
                    return code
            else:
                return '406'
        else:
            pass
        return code
    
    def doWebElement(self, webElement, typeAction='click', message='', timeout = 2, max_iteractions=35):
        if webElement == -1: return False
        if typeAction == 'click':
            flat = 0
            while flat<max_iteractions:
                time.sleep(timeout)
                if 'disable' in webElement.get_attribute('class'):
                    flat += 1
                else:
                    flat = max_iteractions
            else:
                if 'disable' in webElement.get_attribute('class'): return False
                try:
                    webElement.click()
                    return True
                except:
                    self.driver.execute_script("arguments[0].click();", webElement)
                    return True
        elif typeAction == 'write':
            flat = 0
            while flat<max_iteractions:
                time.sleep(timeout)
                try:
                    webElement.send_keys(message)
                    flat = max_iteractions
                    return True
                except:
                    flat += 1
            else:
                return False
        elif typeAction == 'Enter':
            flat = 0
            while flat<max_iteractions:
                time.sleep(timeout)
                try:
                    webElement.send_keys(Keys.ENTER)
                    time.sleep(1)
                    flat = max_iteractions
                    return True
                except:
                    flat += 1
            else:
                return False
        else: 
            pass
    """ Function of delay while a page changes to another
        Parameters:
            url:
            timeout_:
            interactions:
        Return:
            Boolean: True or False depends if the page changes or not.
    """
    def pageChange(self, url, timeout_=2, interactions=5):
        flat = 0 
        while flat<interactions:
            time.sleep(timeout_)
            if url != self.driver.current_url:
                return True
            else:
                flat += 1 
        else:
            return False              
    
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

    def requireScroll(self):
        self.driver.maximize_window()
        SP = self.driver.find_element(By.XPATH, "//body").rect
        SW = self.driver.get_window_size()
        if SP['height']>(1.1*SW['height']):
            return True
        else:
            return False
        
    def existWebElement(self, webElement='email', XPATH_=None, time_=1):
        if webElement=='email':
            try:
                #emails = self.driver.find_elements(By.XPATH,'//input[@type="email"]|//input[contains(@name,"user")]|//input[contains(@name,"login")]|//input[contains(@name,"session")]|//input[contains(@name,"email")]')
                emails = WebDriverWait(self.driver, time_).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[@type="email"]|//input[contains(@name,"user")]|//input[contains(@name,"login")]|//input[contains(@name,"session")]|//input[contains(@name,"email")]')))
                for email in emails:
                    if not email.is_displayed():
                        emails.remove(email)
                if len(emails)>0:
                    return True, emails[0]
                else:
                    return False, None
            except:
                return False, None
        elif webElement=='password':
            try:
                #passwords = self.driver.find_elements(By.XPATH,'//input[@type="password"]')
                passwords = WebDriverWait(self.driver, time_).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[@type="password"]')))
                for password in passwords:
                    if not password.is_displayed():
                        passwords.remove(password)
                if len(passwords)>0:
                    return True, passwords[0]
                else:
                    return False, None
            except:
                return False, None
        elif webElement=='submit':
            try:
                #buttons = self.driver.find_elements(By.XPATH,'//button[@type="button"]|//button[@type="submit"]|//input[@type="submit"]|//button[contains(@id,"submit")]')
                buttons = WebDriverWait(self.driver, time_).until(EC.visibility_of_any_elements_located((By.XPATH,'//button[@type="button"]|//button[@type="submit"]|//input[@type="submit"]|//button[contains(@id,"submit")]')))
                for button in buttons:
                    if not button.is_displayed():
                        buttons.remove(button)
                if len(buttons)>0:
                    return True, buttons[0]
                else:
                    return False, None
            except:
                return False, None
        elif webElement=='verify':
            try:
                #texts = self.driver.find_elements(By.XPATH, '//div[contains(text(),"Enviar un mensaje de texto al")]')
                texts = WebDriverWait(self.driver, time_).until(EC.visibility_of_any_elements_located((By.XPATH, '//div[contains(text(),"Enviar un mensaje de texto al")]')))
                for text in texts:
                    if not text.is_displayed():
                        texts.remove(text)
                if len(texts)>0:
                    return True, texts[0]
                else:
                    return False, None
            except:
                return False, None
        elif webElement=='code':
            try:
                #codes = self.driver.find_elements(By.XPATH, '//input[contains(@name,"code")]|//input[contains(@id,"code")]|//input[contains(@placeholder,"code")]|//input[contains(@placeholder,"Código")]')
                codes = WebDriverWait(self.driver, time_).until(EC.visibility_of_any_elements_located((By.XPATH, '//input[contains(@name,"code")]|//input[contains(@id,"code")]|//input[contains(@placeholder,"code")]|//input[contains(@placeholder,"Código")]')))
                for code in codes:
                    if not code.is_displayed():
                        codes.remove(code)
                if len(codes)>0:
                    return True, codes[0]
                else:
                    return False, None
            except:
                return False, None
        elif webElement=='other':
            try:
                OAuthWait = WebDriverWait(self.driver, time_).until(EC.visibility_of_any_elements_located((By.XPATH,XPATH_)))
                for OAuth in OAuthWait:
                    if not OAuth.is_displayed():
                        OAuth.remove(code)
                if len(OAuthWait)>0:
                    return True, OAuthWait[0]
                else:
                    return False, None
            except:
                return False, None
        else:
            return False, None
        
    def isLoginPage(self):
        for loginWord in LOGIN:
            if loginWord.casefold() in self.driver.title.casefold() and not self.isVerifyPage():
                return True
        else:
            exist,  h = self.existWebElement(time_=0)
            exist_, h = self.existWebElement('password', time_=0)
            if exist or exist_:
                return True
            else:
                return False
        # We requiere a process to determine if a webpage is a login page throught scraping and crawling.
        #I need to implement verification by structure basic, Login Page: input mail and button submit
        
    def isVerifyPage(self):
        for verify_word in VERIFY:
            if verify_word.casefold() in self.driver.title.casefold():
                return True
        else:
            exist,  h = self.existWebElement('verify', time_=5)
            exist_, h = self.existWebElement('code', time_=0)
            if exist or exist_:
                return True
            else:
                return False
            
    def login(self, url, user, password):
        login = False
        self.setDriver(url)
        while True:
            login = self.doLogin(user, password)
            time.sleep(7)
            self.authFail = self.auth_alert()
            if login or self.authFail:
                if self.authFail:
                    print('Ha habido un problema de authenticación')
                    return False
                else:
                    return True
            elif not login and not self.startLog:
                return False
        
    def doLogin(self, user, password):
        if self.isLoginPage():
            if not self.startLog: self.startLog = True 
            e,  email  = self.existWebElement()
            e_, passwd = self.existWebElement('password', time_=0)
            if e and e_:
                email.clear()
                passwd.clear()
                email.send_keys(user)
                passwd.send_keys(password+Keys.ENTER)
            elif e:
                email.clear()
                email.send_keys(user+Keys.ENTER)
            elif e_:
                passwd.clear()
                passwd.send_keys(password+Keys.ENTER)
            else:
                e, OAuthWait = self.existWebElement('other','//*[contains(text(),"Approve sign") or contains(text(),"Aprobar")]', time_=0)
                if e:
                    self.approve = True
                else:
                    self.approve = False
        elif self.isVerifyPage():
            e,  verify = self.existWebElement('verify')
            e_, code   = self.existWebElement('code', time_=0)
            if e:
                verify.click()
                self.reqCode = False
            elif e_:
                self.reqCode = True
                if self.code != None and self.code != '':
                    code.send_keys(self.code+Keys.ENTER)
                    self.reqCode = False
                    self.code = None
            # else:
            #     self.reqCode = True
            #     if not self.code == None and not self.code == '':
            #         code.send_keys(self.code+Keys.ENTER)
            #         self.reqCode = False
            #         self.code = None
        elif self.driver.title == 'Hello':
            try:
                self.driver.find_element(By.PARTIAL_LINK_TEXT,'Taboola Ads').click()
            except Exception:
                self.authFail = True
        elif self.driver.title == '[m]insights - Market Stats':
            try:
                WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//button[contains(text(),"Got it")]'))).click()
            except:
                if self.startLog:
                    return True
                else:
                    return False
        else:
            if self.startLog:
                return True
            else:
                return False
        return False
    
    def auth_alert(self, time_=1):
        try:
            alert = WebDriverWait(self.driver, time_).until(EC.visibility_of_any_elements_located((By.XPATH, "//*[contains(@class,'error') or contains(@id, 'Error') or contains(@id, 'error')]|//input[@aria-invalid='true']|//div[contains(@class,'error')]|//*[contains(text(),'No tenemos noticias') or contains(text(),'denegada') or contains(text(),'hear from you') or contains(text(),'denied')]")))
            for alert_ in alert:
                if not alert_.is_displayed():
                    alert.remove(alert_)
            if len(alert)>0:
                return True
            else:
                return False
        except:
            return False

    def deleteItemList(self, list_, item, WE=True):
        if WE:
            for webElement in list_:
                if webElement.get_attribute('textContent') == item:
                    list_.remove(webElement)
        else:
            for i in range(list_.count(item)):
                list_.pop(list_.index(item))
                
    """
        This method create a pixel in a specific platform.
        Parameters:
            advertiserId:
            pixelName:
            platform:
            pixelType:
            customVariable:
            event:
            pathURL:
        Return:
            snippet code of the pixel or errorCode.    
    """ 
    def createPixel(self, advertiserId, pixelName, platform=0, pixelType='RTG', customVariable='u/p', event_=False, pathURL=None):
        if platform == 0 and pixelType == 'RTG':
            query = 'advertiser_id=%s' % advertiserId
            self.setDriver(urlparse('https://invest.xandr.com/dmp/segments/new')._replace(query=query).geturl())
            name, nameError = self.getWebElement('XPATH', '//input[@placeholder="Enter a segment name"]')
            if name != -1: name[0].send_keys(pixelName)
            save, saveError = self.getWebElement('XPATH', '//button/span[contains(text(),"Save")]')
            if save == -1 or name == -1:
                return 'P401'
            current_url = self.driver.current_url
            save[0].click()
            if self.pageChange(current_url):
                pixelId = urlparse(self.driver.current_url).path.split('/')[-1]
                if pixelId.isdigit():
                    snipet_pixel = """<!-- Segment Pixel - %s - DO NOT MODIFY -->\n<script src="https://secure.adnxs.com/seg?add=%s&t=1" type="text/javascript"></script>\n<!-- End of Segment Pixel -->"""%(pixelName, pixelId)   
                    return  snipet_pixel
                else:
                    return 'P402'
            else:
                return 'P403'
        elif platform == 0 and pixelType=='CONV':
            query = 'id=%s' % advertiserId
            self.setDriver(urlparse('https://invest.xandr.com/pixel')._replace(query=query).geturl())
            new, newError = self.getWebElement('XPATH', '//button/span[contains(text(),"New")]')
            if new == -1: return 'P401'
            if self.doWebElement(new[0]):
                name, nameError = self.getWebElement('XPATH', '//input[contains(@class,"PixelModal-name")]')
                if name != -1: name[0].send_keys(pixelName)
                eventCategory, eventCategoryError = self.getWebElement('XPATH', '//span[contains(text(),"Select...") or contains(text(),"View an item") or contains(text(),"Add to cart") or contains(text(),"Initiate checkout") or contains(text(),"Add payment info") or contains(text(),"Purchase") or contains(text(),"Generate lead")]')
                if eventCategory != -1: eventCategory[0].click()
                category, categoryError = self.getWebElement('XPATH', '//div[contains(text(),"Generate lead")]')
                if category != -1: category[0].click()
                conversion, conversionError = self.getWebElement('XPATH', '//div[contains(text(),"Count all conversions per user")]')
                if conversion != -1: conversion[0].click()
                save, saveError = self.getWebElement('XPATH', '//button/span[contains(text(),"Save")]')
                if save == -1 or name == -1 or eventCategory == -1 or category == -1 or conversion == -1:
                    return 'P401'
                save[0].click()
                new_query = '//span[contains(@title,"%s")]'%pixelName
                pixel, pixelError = self.getWebElement('XPATH', new_query)
                if pixel != -1:
                    try: 
                        pixelId = re.findall(r'-?\d+\.?\d*', pixel[0].get_attribute('title'))[0]
                        snipet_pixel = """<!-- Conversion Pixel - %s - DO NOT MODIFY -->\n<script src="https://secure.adnxs.com/px?id=%s&t=1" type="text/javascript"></script>\n<!-- End of Conversion Pixel -->"""%(pixelName, pixelId)
                        return  snipet_pixel
                    except:
                        return 'P402'
                else:
                    return 'P402'
            else:
                return 'P404'
            
            #WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,'//button/span[contains(text(),"New")]')))[0].click()
            #WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@class,"PixelModal-name")]')))[0].send_keys(pixelName)
            #WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,'//span[contains(text(),"Select...") or contains(text(),"View an item") or contains(text(),"Add to cart") or contains(text(),"Initiate checkout") or contains(text(),"Add payment info") or contains(text(),"Purchase") or contains(text(),"Generate lead")]')))[0].click()
            #WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,'//div[contains(text(),"Generate lead")]')))[0].click()
            #WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,'//div[contains(text(),"Count all conversions per user")]')))[0].click()
            #WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,'//button/span[contains(text(),"Save")]')))[0].click()
            #new_query = '//span[contains(@title,"%s")]'%pixelName
            #pixelId = re.findall(r'-?\d+\.?\d*', WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,new_query)))[0].get_attribute('title'))[0]
            #snipet_pixel = """<!-- Conversion Pixel - %s - DO NOT MODIFY -->\n<script src="https://secure.adnxs.com/px?id=%s&t=1" type="text/javascript"></script>\n<!-- End of Conversion Pixel -->"""%(pixelName, pixelId)   
            #return  snipet_pixel
        elif platform == 1:
            self.setDriver('https://displayvideo.google.com/')
            #self.driver.find_elements(By.XPATH,'//material-button[contains(@class,"search")]')[0].click()
            iconSearch, iconSearchError = self.getWebElement('XPATH', '//material-button[contains(@class,"search _ngcontent")]')
            if iconSearch != -1: iconSearch[0].click() 
            search, searchError = self.getWebElement('XPATH', '//input[contains(@placeholder,"Search by name or ID")]')
            url = self.driver.current_url
            if search != -1:
                search[0].send_keys(advertiserId)
                self.doWebElement(search[0], 'Enter')
            if not self.waitChangeURL(url): return '405'
            try:
                marketId, h = re.findall(r'-?\d+\.?\d*',self.driver.current_url)
            except:
                return '405'
            if iconSearch == -1 or search == -1: return '401'
            if self.existFloodlight(pixelName, marketId, advertiserId, 10): return '403'
            fragment = 'ng_nav/p/%s/a/%s/fl/details'%(marketId,advertiserId)
            self.setDriver(urlparse(self.driver.current_url)._replace(fragment=fragment).geturl())
            existU = self.existVariableDV360('u')
            existP = self.existVariableDV360('p')
            if not existU and not existP:
                self.createCustomVariable_('u')
                self.createCustomVariable_('p')
            elif not existU:
                self.createCustomVariable_('u')
            elif not existP:
                self.createCustomVariable_('p')
            fragment = 'ng_nav/p/%s/a/%s/fl/events/new'%(marketId,advertiserId)
            self.setDriver(urlparse(self.driver.current_url)._replace(fragment=fragment).geturl())
            
            web, webError = self.getWebElement('XPATH', '//div[contains(@id,"entity-type-card-activityWeb")]')
            if web != -1: 
                web[0].click()
            else:
                return '401'
            name, nameError = self.getWebElement('XPATH', '//input[contains(@debugid,"acx_177925851_179054344")]')
            if name != -1: name[0].send_keys(pixelName)
            formatt, formattError = self.getWebElement('XPATH', '//div[contains(text(),"Image tag")]')
            if formatt != -1: formatt[0].click()
            typee, typeeError = self.getWebElement('XPATH', '//div[contains(text(),"Counter")]')
            if typee != -1: typee[0].click()
            counting, countingError = self.getWebElement('XPATH', '//div[contains(text(),"Standard")]')
            if counting != -1: counting[0].click()
            exclude, excludeError = self.getWebElement('XPATH', '//div[contains(text(),"exclude")]')
            if exclude != -1: self.doWebElement(exclude[0])
            remarketing, remarketingError = self.getWebElement('XPATH', '//div[contains(text(),"Enable this Display & Video 360 activity for remarketing.")]')
            if remarketing != -1: self.doWebElement(remarketing[0])
            #Linked custom variables process
            iconCustom, iconCustomError = self.getWebElement('XPATH', '//material-icon[@id="open-custom-variables-icon"]')
            if name == -1 or formatt == -1 or typee == -1 or counting == -1 or exclude == -1 or remarketing == -1 or iconCustom == -1: return '401'
            if iconCustom != -1: self.doWebElement(iconCustom[0])
            if customVariable == 'u/p':
                existU, indexU = self.existVariable('u')
                existP, indexP = self.existVariable('p')
                customs, customsError = self.getWebElement('XPATH', '//picker-tree/div/material-checkbox')
                if customs != -1:
                    customs[indexU].click()
                    customs[indexP].click()
            else:
                exist, index = self.existVariable(customVariable)
                customs, customsError = self.getWebElement('XPATH', '//picker-tree/div/material-checkbox')
                if customs != -1: customs[index].click()
            save, saveError = self.getWebElement('XPATH','//material-button[contains(@id,"save-button")]')
            if save != -1: self.doWebElement(save[1])
            #save[1].click()
            time.sleep(5)
            url = self.driver.current_url
            save, saveError = self.getWebElement('XPATH','//material-button[contains(@id,"save-button")]')
            if save != -1: self.doWebElement(save[0])
            alert, error = self.getWebElement('XPATH', '//div[contains(text(),"Floodlight activity name is not unique")]', 1, max_iteractions=10)
            if alert != -1:
                if not self.waitChangeURL(url): return '402'
                try:
                    marketId, advertiserId, floodlightId = re.findall(r'-?\d+\.?\d*',self.driver.current_url)
                except:
                    time.sleep(2)
                    marketId, advertiserId, floodlightId = re.findall(r'-?\d+\.?\d*',self.driver.current_url)
                url = self.driver.current_url
                fragment = 'ng_nav/p/%s/a/%s/fl/fle/%s/code'%(marketId,advertiserId,floodlightId)
                self.setDriver(urlparse(self.driver.current_url)._replace(fragment=fragment).geturl())
                if not self.waitChangeURL(url): return '402'
                snippet, snippetError = self.getWebElement('XPATH','//div[contains(@class,"mirror-text") and contains(@class,"_ngcontent")]', visible = False)
                return  snippet
            else:
                snippet = self.getSnippetCode(advertiserId, pixelName, 'DV360')
                return  snippet
        elif platform == 2 and pixelType=='RTG' and not event_:
            query = 'accountId=%s' % advertiserId
            self.setDriver(urlparse('https://ads.taboola.com/audiences/pixel-based/new')._replace(query=query).geturl())
            webElement, error = self.getWebElement('XPATH', '//button/span[contains(text(),"+ New Audience")]')
            webElement[0].click()
            webElement, error = self.getWebElement('XPATH', '//button/span[contains(text(),"Continue")]')
            webElement[0].click()
            webElement, error = self.getWebElement('XPATH', '//div[@id="name"]')
            if webElement !=-1: webElement[0].send_keys(pixelName)
            webElement, error = self.getWebElement('XPATH', '//input[contains(@placeholder,"URL Address")]')
            if webElement != -1:
                if 'HomePV' in pixelName:
                    operator, error = self.getWebElement('XPATH', '//span[contains(text(),"Contains")]')
                    operator[0].click()
                    operator, error = self.getWebElement('XPATH', '//span[contains(text(),"Equals")]')
                    operator[0].click()
                    URL = pathURL[:-1] if pathURL[-1] == '/' else pathURL
                    webElement[0].send_keys(URL)
                else:
                    webElement[0].send_keys(pathURL)
                webElement, error = self.getWebElement('XPATH', '//button/span[contains(text(),"ADD")]')
                if webElement != -1: webElement[0].click()
            exclude, error = self.getWebElement('XPATH', '//div[@id="exclude-audience"]')
            exclude[0].find_elements(By.XPATH, 'label')[1].click()
            webElement, error = self.getWebElement('XPATH', '//button/span[contains(text(),"Create Audience")]')
            if webElement != -1: webElement[0].click()
            webElement, error = self.getWebElement('XPATH', '//span[contains(text(),"This Audience Name already exists")]', timeout_=1)
            if webElement != -1: 
                return 'No TAG'
            else:
                return 'NO TAG'
            #WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//div[@id="name"]')))[0].send_keys(pixelName)
            #WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH,'//input[contains(@placeholder,"URL Address")]'))).send_keys('/test')
            #WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH,'//button/span[contains(text(),"ADD")]'))).click()
            #WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//button/span[contains(text(),"Create Audience")]')))[0].click()
            #return 'Test_Taboola'
        elif platform == 2 and pixelType=='RTG' and event_:
            query = 'accountId=%s' % advertiserId
            self.setDriver(urlparse('https://ads.taboola.com/audiences/pixel-based/new')._replace(query=query).geturl())
            webElement, error = self.getWebElement('XPATH', '//button/span[contains(text(),"+ New Audience")]')
            webElement[0].click()
            webElement, error = self.getWebElement('XPATH', '//button/span[contains(text(),"Continue")]')
            webElement[0].click()
            webElement, error = self.getWebElement('XPATH', '//div[@id="name"]')
            if webElement !=-1: webElement[0].send_keys(pixelName)
            audienceType, error = self.getWebElement('XPATH', '//div[@id="audience-type"]')
            audienceType[0].find_elements(By.XPATH, 'label')[1].click()
            webElement, error = self.getWebElement('XPATH', '//div[@id="based-on-events"]', timeout_=1)
            eventName = pixelName.split('_',1)[1] if len(pixelName.split('_',1))>1 and not pixelName.split('_',1)[1].isdigit() else pixelName
            if webElement !=-1: 
                tableEvents, error = self.getWebElement('XPATH', '//div[@class="ag-pinned-left-cols-container"]')
                if tableEvents !=-1:
                    events = tableEvents[0].find_elements(By.XPATH, 'div')
                    if len(events)>0:
                        for event in events:
                            eventName_ = event.text.split('\n')[0]
                            if eventName == eventName_:
                                event.click()
                                break
                        else:
                            webElement[0].find_elements(By.XPATH,'label')[1].click()
                            webElement, error = self.getWebElement('XPATH', '//div[@id="eventName"]')
                            webElement[0].send_keys(eventName)
                            webElement, error = self.getWebElement('XPATH', '//code[@class="code-snippet-text"]')
                            snippet = webElement[0].text
                            exclude, error = self.getWebElement('XPATH', '//div[@id="exclude-audience"]')
                            exclude[0].find_elements(By.XPATH, 'label')[1].click()
                            webElement, error = self.getWebElement('XPATH', '//button/span[contains(text(),"Create Audience")]')
                            if webElement != -1: webElement[0].click()
                            existAudience, error = self.getWebElement('XPATH', '//span[contains(text(),"This Audience Name already exists")]', timeout_=1)
                            if existAudience != -1: 
                                return "<!-- Taboola Pixel Code -->\n<script>\n    _tfa.push({notify: 'event', name: '%s', id: %s});\n</script>\n<!-- End of Taboola Pixel Code -->"%(eventName, advertiserId)
                            else: 
                                return snippet       
                    else:
                        webElement[0].find_elements(By.XPATH,'label')[1].click()
                        webElement, error = self.getWebElement('XPATH', '//div[@id="eventName"]')
                        webElement[0].send_keys(eventName)
                        webElement, error = self.getWebElement('XPATH', '//code[@class="code-snippet-text"]')
                        snippet = webElement[0].text
                        exclude, error = self.getWebElement('XPATH', '//div[@id="exclude-audience"]')
                        exclude[0].find_elements(By.XPATH, 'label')[1].click()
                        webElement, error = self.getWebElement('XPATH', '//button/span[contains(text(),"Create Audience")]')
                        if webElement != -1: webElement[0].click()
                        existAudience, error = self.getWebElement('XPATH', '//span[contains(text(),"This Audience Name already exists")]', timeout_=1)
                        if existAudience != -1: 
                            return "<!-- Taboola Pixel Code -->\n<script>\n    _tfa.push({notify: 'event', name: '%s', id: %s});\n</script>\n<!-- End of Taboola Pixel Code -->"%(eventName, advertiserId) 
                        else: 
                            return snippet
            else:
                webElement, error = self.getWebElement('XPATH', '//div[@id="eventName"]')
                webElement[0].send_keys(eventName)
                webElement, error = self.getWebElement('XPATH', '//code[@class="code-snippet-text"]')
                snippet = webElement[0].text
                exclude, error = self.getWebElement('XPATH', '//div[@id="exclude-audience"]')
                exclude[0].find_elements(By.XPATH, 'label')[1].click()
                webElement, error = self.getWebElement('XPATH', '//button/span[contains(text(),"Create Audience")]')
                if webElement != -1: webElement[0].click()
                existAudience, error = self.getWebElement('XPATH', '//span[contains(text(),"This Audience Name already exists")]', timeout_=1)
                existEvent, error = self.getWebElement('XPATH', '//span[contains(text(),"This Event Name already exists")]', timeout_=1)
                if existAudience == -1 and existEvent == -1: 
                    return snippet
                else: 
                    return "<!-- Taboola Pixel Code -->\n<script>\n    _tfa.push({notify: 'event', name: '%s', id: %s});\n</script>\n<!-- End of Taboola Pixel Code -->"%(eventName, advertiserId)
        elif platform == 2 and pixelType=='CONV' and event_:
            query = 'accountId=%s' % advertiserId
            self.setDriver(urlparse('https://ads.taboola.com/conversions')._replace(query=query).geturl())
            time.sleep(10)
            iframe = WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//div/iframe[contains(@title,"Tracking")]')))
            self.driver.switch_to.frame(iframe[0])
            #time.sleep(5)
            #WebDriverWait(self.driver, 60).until(EC.visibility_of_any_elements_located((By.XPATH,'//a[@id="btn-new-rule"]')))[0].click()
            createNew, error = self.getWebElement('XPATH', '//a[@id="btn-new-rule"]')
            self.doWebElement(createNew[0])
            event, error = self.getWebElement('XPATH', '//button[contains(text(),"Event")]')
            self.doWebElement(event[0])
            webElement, error = self.getWebElement('XPATH', '//button[contains(text(),"Custom")]')
            self.doWebElement(webElement[0])
            #time.sleep(10)
            #WebDriverWait(self.driver, 60).until(EC.visibility_of_any_elements_located((By.XPATH,'//a[@id="btn-new-rule"]')))[0].click()
            #WebDriverWait(self.driver, 60).until(EC.visibility_of_any_elements_located((By.XPATH,'//button[contains(text(),"Event")]')))[0].click()
            #WebDriverWait(self.driver, 60).until(EC.visibility_of_any_elements_located((By.XPATH,'//button[contains(text(),"Custom")]')))[0].click()
            WebDriverWait(self.driver, 60).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[@id="conversionName"]')))[0].send_keys(pixelName)
            eventName = pixelName.split('_',1)[1] if len(pixelName.split('_',1))>1 and not pixelName.split('_',1)[1].isdigit() else pixelName
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[@id="eventName"]')))[0].clear()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[@id="eventName"]')))[0].send_keys(eventName)
            Select(self.driver.find_element(By.XPATH,'//select[contains(@id,"conversionCategory")]')).select_by_index(8)
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//button[@data-name="excludeFromCampaigns"]')))[0].click()
            snippet = self.driver.find_element(By.XPATH,'//textarea[@id="codeSnippet"]').get_attribute('value')
            webElement, error = self.getWebElement('XPATH', '//button[@id="save"]')
            if webElement != -1: webElement[0].click()
            alert_error, error = self.getWebElement('XPATH', '//div[contains(@class,"alert-error")]', timeout_=1)
            if alert_error != -1:
                self.driver.switch_to.default_content()
                return "<!-- Taboola Pixel Code -->\n<script>\n    _tfa.push({notify: 'event', name: '%s', id: %s});\n</script>\n<!-- End of Taboola Pixel Code -->"%(eventName,advertiserId)
            else:
                self.driver.switch_to.default_content()
                return snippet
            #self.driver.switch_to.default_content()
            #return snippet
        elif platform == 2 and pixelType=='CONV' and not event_:
            query = 'accountId=%s' % advertiserId
            self.setDriver(urlparse('https://ads.taboola.com/conversions')._replace(query=query).geturl())
            iframe, error = self.getWebElement('XPATH', '//div/iframe[contains(@title,"Tracking")]')
            if iframe != -1: self.driver.switch_to.frame(iframe[0])
            #time.sleep(30)
            #print('Hemos terminado la espera')
            createNew, error = self.getWebElement('XPATH', '//a[@id="btn-new-rule"]')
            self.doWebElement(createNew[0])
            #createNew[0].click()
            webElement, error = self.getWebElement('XPATH', '//input[@placeholder="advertiser.com/thank-you"]', visible=False) 
            if webElement != -1:
                if 'HomePV' in pixelName:
                    operator, error = self.getWebElement('XPATH', '//button/span[contains(text(),"contains")]')
                    if operator != -1: operator[0].click()
                    option, error = self.getWebElement('XPATH', '//a[contains(text(),"equals")]')
                    if option != -1: option[0].click()
                    URL = pathURL[:-1] if pathURL[-1] == '/' else pathURL
                    try:
                        webElement[-1].send_keys(URL)
                    except:
                        webElement, error = self.getWebElement('XPATH', '//input[@placeholder="advertiser.com/thank-you"]', visible=False)
                        webElement[-1].send_keys(URL)
                else:
                    if not self.doWebElement(webElement[-1], typeAction='write', message=pathURL):
                        webElement, error = self.getWebElement('XPATH', '//input[@placeholder="advertiser.com/thank-you"]', visible=False)
                        if not self.doWebElement(webElement[-1], typeAction='write', message=pathURL):
                            return '404'
            #webElement, error = self.getWebElement('XPATH', '//button[@id="addUrlConversion"]')
            #if webElement != -1: webElement[0].click()
            webElement, error = self.getWebElement('XPATH', '//input[@id="conversionName"]')
            webElement[0].send_keys(pixelName)
            webElement, error = self.getWebElement('XPATH', '//select[@id="conversionCategory"]')
            if webElement != -1: Select(webElement[0]).select_by_index(8)
            webElement, error = self.getWebElement('XPATH', '//button[@id="save"]')
            if webElement != -1: webElement[0].click()
            alert_error, error = self.getWebElement('XPATH', '//div[contains(@class,"alert-error")]', timeout_=1)
            print(alert_error)
            if alert_error != -1:
                self.driver.switch_to.default_content()
                return 'Exist'
            else:
                self.driver.switch_to.default_content()
                return 'No Tag'
        elif platform == 3:
            fragment = 'client/%s/activities' % advertiserId
            self.setDriver(urlparse('https://amerminsights.mplatform.com')._replace(fragment=fragment).geturl())
            iframe = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//div/iframe[contains(@class,"external-iframe")]')))
            self.driver.switch_to.frame(iframe)
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//button[contains(@id,"createButton") and contains(text(),"Create Activity")]'))).click()
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//input[@id="name"]'))).send_keys(pixelName)
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//span[contains(text(),"for Consumer Correlation")]'))).click()
            if customVariable == 'u/p':
                WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"customvariable_")]')))[0].send_keys('p')
                WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"variableId")]')))[0].send_keys('p')
                WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//a[contains(text(),"add")]')))[0].click()
                WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"customvariable_")]')))[1].send_keys('u')
                WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"variableId")]')))[1].send_keys('u')
                WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//a[contains(text(),"add")]')))[0].click()
            else:
                WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"customvariable_")]')))[0].send_keys(customVariable)
                WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"variableId")]')))[0].send_keys(customVariable)
                WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//a[contains(text(),"add")]')))[0].click()  
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//div[contains(text(),"SAVE")]'))).click()
            try:
                WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,"//div[contains(text(),'Duplicate')]")))
                WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,"//div/i[contains(@class,'close')]")))[0].click()
            except:
                pass
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//input[contains(@placeholder,"Search...")]'))).send_keys(pixelName+Keys.ENTER)
            time.sleep(10)
            WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.XPATH,'//i[@class="js-activity-tag turbine tag link icon"]'))).click()
            snippet = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//textarea[@id="activityTagCode"]'))).get_attribute('value')
            self.driver.switch_to.default_content()
            return snippet
        return 'No pixel'
    
    def getSnippetCode(self, advertiserId, pixelName, platform):
        if platform == 'Xandr Seg':
            query = 'advertiser_id=%s' % advertiserId
            self.setDriver(urlparse('https://invest.xandr.com/dmp/segments/')._replace(query=query).geturl())
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//input[contains(@placeholder,"Search Name or ID")]'))).send_keys(pixelName+Keys.ENTER)
            segments = WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//div[contains(@class,"dmp-Segments-Segment-Name")]')))
            if len(segments)>1:
                for segment in segments:
                    if segment.text == pixelName:
                        segment.click()
                        pixelId = urlparse(self.driver.current_url).path.split('/')[-1]
                        snippet = """<!-- Segment Pixel - %s - DO NOT MODIFY -->\n<script src="https://secure.adnxs.com/seg?add=%s&t=1" type="text/javascript"></script>\n<!-- End of Segment Pixel -->"""%(pixelName, pixelId)
                        return snippet
                else:
                    return -1
            elif len(segments)>0:
                segments[0].click()
                pixelId = urlparse(self.driver.current_url).path.split('/')[-1]
                snippet = """<!-- Segment Pixel - %s - DO NOT MODIFY -->\n<script src="https://secure.adnxs.com/seg?add=%s&t=1" type="text/javascript"></script>\n<!-- End of Segment Pixel -->"""%(pixelName, pixelId)
                return snippet
            else:
                return -1
        elif platform == 'Xandr Conv':
            query = 'id=%s' % advertiserId
            self.setDriver(urlparse('https://invest.xandr.com/pixel')._replace(query=query).geturl())
            time.sleep(10)
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//span[text()="10"]'))).click()
            WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH,'//div[text()="100"]'))).click()
            time.sleep(10)
            rows = WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//table/tbody/tr')))
            print(len(rows))
            if len(rows)>1:
                for row in rows:
                    columns = row.find_elements(By.XPATH,'td')
                    if columns[1].text.replace('\n','') == pixelName:
                        pixelId = columns[2].text
                        snippet = """<!-- Conversion Pixel - %s - DO NOT MODIFY -->\n<script src="https://secure.adnxs.com/px?id=%s&t=1" type="text/javascript"></script>\n<!-- End of Conversion Pixel -->"""%(pixelName, pixelId)
                        return snippet
                else:
                    return -1
            elif len(rows)>0:
                columns = rows[0].find_elements(By.XPATH,'td')
                pixelId = columns[2].text
                snippet = """<!-- Segment Pixel - %s - DO NOT MODIFY -->\n<script src="https://secure.adnxs.com/seg?add=%s&t=1" type="text/javascript"></script>\n<!-- End of Segment Pixel -->"""%(pixelName, pixelId)
                return snippet
            else:
                return -1
        elif platform == 'DV360':
            self.setDriver('https://displayvideo.google.com/')
            iconSearch, iconSearchError = self.getWebElement('XPATH', '//material-button[contains(@class,"search _ngcontent")]')
            if iconSearch != -1: iconSearch[0].click() 
            search, searchError = self.getWebElement('XPATH', '//input[contains(@placeholder,"Search by name or ID")]')
            url = self.driver.current_url
            if search != -1:
                search[0].send_keys(advertiserId)
                self.doWebElement(search[0], 'Enter')
            if not self.waitChangeURL(url, 5): return '405'
            try:
                marketId, h = re.findall(r'-?\d+\.?\d*',self.driver.current_url)
            except:
                return '402'
            if iconSearch == -1 or search == -1: return '401'
            url = self.driver.current_url
            fragment = 'ng_nav/p/%s/a/%s/fl/events'%(marketId,advertiserId)
            self.setDriver(urlparse(self.driver.current_url)._replace(fragment=fragment).geturl())
            if not self.waitChangeURL(url, 5): return '405'
            removeFilter, removeFilterError = self.getWebElement('XPATH','//material-button[contains(@aria-label,"Remove all filters")]', timeout_=1)
            if removeFilter != -1: removeFilter[0].click()
            search, searchError = self.getWebElement('XPATH','//input[contains(@class,"search-box")]')
            if search != -1:
                search[0].send_keys(pixelName+Keys.ENTER)
            else:
                addFilter, addFilterError  = self.getWebElement('XPATH','//material-fab[contains(@class,"filter-bar-toggle")]')
                if addFilter != -1: 
                    addFilter[0].click()
                    search, searchError = self.getWebElement('XPATH','//input[contains(@class,"search-box")]')
                    if search != -1:
                        search[0].send_keys(pixelName+Keys.ENTER)
                    else:
                        return '401'
                else:
                    return '401'
            self.waitChange((By.XPATH,'//div[contains(@class,"ess-table-canvas")]'), 'class', 'content-loading', 5)
            webElement, error = self.getWebElement('XPATH','//div[contains(text(),"Show rows:")]')
            if webElement != -1: self.driver.execute_script("arguments[0].scrollIntoView();", webElement[0])
            table, tableError = self.getWebElement('XPATH', '//div[contains(@class,"ess-table-canvas")]')
            if table != -1:
                floods, floodsError = self.getWebElement('XPATH', 'div/ess-cell/name-id-cell', visible = False, driver = table[0])
                if floods != -1:
                    for flood in floods:
                        nameId = flood.get_attribute('textContent').split('\n')
                        if nameId[1] == pixelName:
                            floodlightId = nameId[2]
                            url = self.driver.current_url
                            fragment = 'ng_nav/p/%s/a/%s/fl/fle/%s/code'%(marketId,advertiserId,floodlightId)
                            self.setDriver(urlparse(self.driver.current_url)._replace(fragment=fragment).geturl())
                            if not self.waitChangeURL(url): return '405'
                            code, codeError = self.getWebElement('XPATH', '//div[contains(@class,"mirror-text") and contains(@class,"_ngcontent")]', visible = False)
                            snippet = code[0].get_attribute('textContent') if code != -1 else '401'
                            return snippet
                    else:
                        return '401'
                else:
                    return '403'
                
            else:
                return '401'
        elif platform == 'Taboola Seg' or platform == 'Taboola Conv':
            pass
        else:
            self.setDriver('https://amerminsights.mplatform.com/#client/%s/activities'%advertiserId)
            iframe = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//div/iframe[contains(@class,"external-iframe")]')))
            self.driver.switch_to.frame(iframe)
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//input[contains(@placeholder,"Search...")]'))).send_keys(pixelName+Keys.ENTER)
            time.sleep(10)
            WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.XPATH,'//i[@class="js-activity-tag turbine tag link icon"]'))).click()
            snippet = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//textarea[@id="activityTagCode"]'))).get_attribute('value')
            self.driver.switch_to.default_content()
            return snippet
        
    def createCustomVariable(self, variable):
        WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-button[contains(@debugid,"creation-button") or contains(text(),"ADD CUSTOM")]')))[0].click()
        WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH, '//div[contains(@class,"particle-table-last-row")]')))[0].click()
        WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH, '//*[contains(@aria-label,"Edit this Name")]')))[0].click()
        WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH, '//input')))[-1].send_keys(variable)
        WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-button[contains(@class,"btn-yes")]')))[0].click()
        WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-button[contains(@id,"save-button")]')))[1].click()
        time.sleep(5)
        WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-button[contains(@id,"save-button")]')))[0].click()

    def existVariable(self, variable, table='picker'):
        if table=='picker':
            variable = ': '+ variable
            try:
                customVariable = WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//picker-tree/div')))
                for i in range(len(customVariable)):
                    if customVariable[i].get_attribute('textContent')[-len(variable):] == variable:
                        return True, i
                else:
                    return False, -1
            except:
                return False, -1
        elif table=='div':
            try:
                customVariable = WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//div[contains(@class,"particle-table-row")]')))
                for i in range(len(customVariable)):
                    if customVariable[i].get_attribute('textContent').split('\n')[1] == variable:
                        return True, i
                else:
                    return False, -1
            except:
                return False, -1
            
    def existVariableDV360(self, variable):
        webElement, error = self.getWebElement('XPATH','//span[starts-with(text(),"u") and contains(text(),": %s")]'%variable)
        if webElement == -1:
            return False
        else:
            for element in webElement:
                customVariable = re.findall(r'u\d+: %s'%variable, element.get_attribute('textContent'))
                if len(customVariable)>0:
                    if customVariable[0] == element.get_attribute('textContent'):
                        return True
            else:
                return False
            
    def createCustomVariable_(self, variable):
        webElement, error = self.getWebElement('XPATH','//material-icon[@id="open-custom-variables-icon"]')
        if webElement != -1:
            webElement[0].click()
            webElement, error = self.getWebElement('XPATH','//material-button[contains(@debugid,"creation-button") or contains(text(),"ADD CUSTOM")]')
            if webElement != -1:
                webElement[0].click()
                webElement, error = self.getWebElement('XPATH','//div[contains(@class,"particle-table-last-row")]')
                webElement[0].click()
                webElement, error = self.getWebElement('XPATH','//*[contains(@aria-label,"Edit this Name")]')
                webElement[0].click()
                webElement, error = self.getWebElement('XPATH','//input')
                webElement[-1].send_keys(variable)
                webElement, error = self.getWebElement('XPATH','//material-button[contains(@class,"btn-yes")]')
                webElement[0].click()
                webElement, error = self.getWebElement('XPATH','//material-button[contains(@id,"save-button")]')
                webElement[1].click()
                time.sleep(5)
                webElement, error = self.getWebElement('XPATH','//material-button[contains(@id,"save-button")]')
                webElement[0].click()
                self.waitWebElement(webElement[0], condition='class')
                return True
            else:
                return False
        else:
            return False
            
    def existAdvertiserId(self, platform_, advertiserId):
        #['Xandr Seg', 'Xandr Conv', 'DV360', 'Taboola', 'minsights']
        if platform_ == 'Xandr Seg' or platform_ == 'Xandr Conv':
            try:
                self.setDriver('https://invest.xandr.com/bmw/advertisers')
                #time.sleep(10)
                search = WebDriverWait(self.driver,10).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@placeholder,"Search")]')))
                #search = self.driver.find_elements(By.XPATH,'//input[@placeholder="Search"]')
                search[0].clear()
                search[0].send_keys(advertiserId+Keys.ENTER)
                try:
                    WebDriverWait(self.driver,30).until(EC.visibility_of_any_elements_located((By.XPATH,'//div/header[contains(text(),"No Data Available")]')))
                    return False
                except:
                    return True
            except:
                print('No esta encontrando el buscador')
                return False
        elif platform_ == 'DV360':
            self.setDriver('https://displayvideo.google.com/')
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//material-button[contains(@class,"search _ngcontent")]')))[0].click()
            search = WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@placeholder,"Search by name or ID")]')))[0]
            preURL = self.driver.current_url
            search.send_keys(advertiserId)
            time.sleep(2)
            search.send_keys(Keys.ENTER)
            time.sleep(3)
            if self.driver.current_url == preURL:
                return False
            else:
                try:
                    marketId, advId = re.findall(r'-?\d+\.?\d*',self.driver.current_url)
                    if advId == advertiserId:
                        return True
                    else:
                        return False
                except:
                    return False
        elif platform_ == 'Taboola Seg' or platform_ == 'Taboola Conv':
            self.setDriver('https://ads.taboola.com/')
            menuAdvertiser, menuAdvertiserError = self.getWebElement('XPATH', '//div[contains(@class,"accountPicker_container__1sNyQ")]')
            if menuAdvertiser != -1: 
                menuAdvertiser[0].click() 
                time.sleep(5)
                search, searchError = self.getWebElement('XPATH', '//input[contains(@id,"react-select-")]')
                if search != -1:
                    current_url = self.driver.current_url
                    search[0].clear()
                    search[0].send_keys(advertiserId)
                    self.doWebElement(search[0],'Enter')
                    self.pageChange(current_url)
                    try:
                        advId = re.findall(r'-?\d+\.?\d*',self.driver.current_url)[0]
                        if advId == advertiserId:
                            return True
                        else:
                            return False
                    except:
                        return False
                else:
                    return False
            else: 
                return False
            
            #WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//div[contains(@class,"accountPicker_container__1sNyQ")]')))[0].click()
            #time.sleep(5)
            #WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"react-select-")]')))[0].clear()
            #WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"react-select-")]')))[0].send_keys(advertiserId)
            #time.sleep(2)
            #WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"react-select-")]')))[0].send_keys(Keys.ENTER)
            #time.sleep(3)
            #try:
            #    advId = re.findall(r'-?\d+\.?\d*',self.driver.current_url)[0]
            #    if advId == advertiserId:
            #        return True
            #    else:
            #        return False
            #except:
            #    return False     
        else:
            return False
        
    """
        This method return the market IF given a valid Advertiser ID.
        Return:
            marketId: String  or -1 if the advertiserId there's not exist.     
    """
    def getDV360MarketId(self, advertiserId):
        self.setDriver('https://displayvideo.google.com/')
        WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//material-button[contains(@class,"search _ngcontent")]')))[0].click()
        search = WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@placeholder,"Search by name or ID")]')))[0]
        search.send_keys(advertiserId)
        time.sleep(2)
        search.send_keys(Keys.ENTER)
        time.sleep(3)
        try:
            marketId, advId = re.findall(r'-?\d+\.?\d*',self.driver.current_url)
            if advId == advertiserId:
                return marketId
            else:
                return -1
        except:
            return -1
    
    """This method implement de Market set-up in Xandr DSP.
            Parameters:
                market: market that we want to set-up in Xandr DSP.
            Return:
                Boolean: True or False if the market set-up was posible.
    """    
    def setMarketXandr(self, market):
        try:
            memberId = MARKETS[market]
        except KeyError:
            return False
        except:
            return False
        
        menu, menuError = self.getWebElement('XPATH', '//div[contains(@id, "rightnav")]')
        if menu != -1: 
            menuMarket, menuMarketError = self.getWebElement('XPATH', 'ul/li', driver=menu[0])
            if menuMarket != -1: 
                if memberId in menuMarket[-1].get_attribute('textContent'): return True
                self.doWebElement(menuMarket[-1])
                switch, switchError = self.getWebElement('XPATH', 'div/ul/button', driver=menuMarket[-1])
                if switch != -1: 
                    self.doWebElement(switch[0])
                else:
                    return False
            else:
                return False
            markets, error = self.getWebElement('XPATH', '//tbody/tr[@class = "nav-lucid-Table-Tr" or contains(@class, "nav-lucid-Table-is-active")]')
            if markets == -1: return False
            for market in markets:
                fields, error = self.getWebElement('XPATH', 'td', driver=market)
                if fields[2].get_attribute('textContent') == memberId:
                    if fields[-1].get_attribute('textContent') != 'Default':
                        self.doWebElement(fields[-1])
                        self.doWebElement(fields[1])
                    else:
                        self.doWebElement(fields[1])
                        closeIcon, error = self.getWebElement('XPATH', '//button[contains(@class,"nav-lucid-Dialog-close-button")]', timeout_=1, max_iteractions=10)
                        try:
                            if closeIcon != -1: self.doWebElement(closeIcon[0])
                        except:
                            pass
                    return True
            else:
                closeIcon, error = self.getWebElement('XPATH', '//button[contains(@class,"nav-lucid-Dialog-close-button")]')
                self.doWebElement(closeIcon[0])
                return False
        else:
            return False
    """
        This method implement a function to search the advertiser in Minsights Platform.
        Return:
            AdvertiserId: String or -1 if the advertiserName there's not exist.     
    """         
    def existMinsightsId(self, advertiserName, advertiserCountry, agency):
        self.setMinsightsAgency(agency)
        try:
            self.setMinsightsCountry(advertiserCountry)
        except:
            return -1
        self.setDriver('https://amerminsights.mplatform.com/#client')
        self.driver.switch_to.default_content()
        iframe = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//div/iframe[contains(@class,"external-iframe")]')))
        self.driver.switch_to.frame(iframe)
        try:
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//input[contains(@placeholder,"Search...")]'))).send_keys(advertiserName+Keys.ENTER)
        except:
            self.driver.switch_to.default_content()
            iframe = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//div/iframe[contains(@class,"external-iframe")]')))
            self.driver.switch_to.frame(iframe)
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//input[contains(@placeholder,"Search...")]'))).send_keys(advertiserName+Keys.ENTER)
        try:
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//td[contains(text(),"No results found")]')))
            self.driver.switch_to.default_content()
            return -1
        except:
            activities = WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//tbody/tr/td/div/a')))
            rows       = WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//tbody/tr')))     
            for activity, row in zip(activities,rows):
                if activity.text == advertiserName or activity.text.casefold() == advertiserName.casefold():
                    id_ = row.find_elements(By.TAG_NAME,'td')[2].text
                    self.driver.switch_to.default_content()
                    return id_
            else:
                self.driver.switch_to.default_content()
                return -1
            
    def setMinsightsCountry(self, advertiserCountry):
        self.setDriver('https://amerminsights.mplatform.com/')
        WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//i')))[1].click()
        WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@placeholder,"Search")]')))[0].clear()
        WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@placeholder,"Search")]')))[0].send_keys(advertiserCountry)
        WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@placeholder,"Search")]')))[0].send_keys(Keys.ENTER)
        
    def setMinsightsAgency(self, agency):
        self.setDriver('https://amerminsights.mplatform.com/')
        try:
            WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.XPATH,'//button[contains(text(),"Got it")]'))).click()
        except:
            pass
        WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//i')))[0].click()
        WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@placeholder,"Search")]')))[0].clear()
        WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@placeholder,"Search")]')))[0].send_keys(agency)
        WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@placeholder,"Search")]')))[0].send_keys(Keys.ENTER)
        
    """ Method that implemented the verification of the pixels in the diferents DSP.
        Parameters:
            platforms:
            advertiserId:
            pixelName:
        Return:
            Boolean: True if the pixelName given exist, False in other case.
    """
    def existPixel(self, platform, advertiserId, pixelName):
        if platform == 'Taboola Seg' or platform == 'Taboola Conv':
            query = 'accountId=%s' % advertiserId
            if platform == 'Taboola Seg':
                #query = query + '&reportId=pixel-based'
                query = query + '&reportId=taboola-pixel-audiences'
                self.setDriver(urlparse('https://ads.taboola.com/audiences')._replace(query=query).geturl())
                filter_, filterError = self.getWebElement('XPATH', '//button[contains(@aria-label,"Remove audienceStatus filter")]')
                if filter_ != -1: filter_[0].click()
                search, searchError = self.getWebElement('XPATH', '//input[contains(@id,"grid-quick-filter")]')
                if search != -1: 
                    search[0].send_keys(pixelName+Keys.ENTER)
                else:
                    return False
                webElement, error = self.getWebElement('XPATH', '//span[contains(text(),"No available data for this selection")]')
                if webElement != -1: return False
                pixels, pixelsError = self.getWebElement('XPATH', '//div[@col-id="taboola-pixel-audiences_audienceName"]')
                if pixels == -1: return False
                for pixel in pixels:
                    if pixelName == pixel.text:
                        return True
                else:
                    return False
            else:
                self.setDriver(urlparse('https://ads.taboola.com/conversions')._replace(query=query).geturl())
                iframe, iframeError = self.getWebElement('XPATH', '//div/iframe[contains(@title,"Tracking")]')
                if iframe != -1: self.driver.switch_to.frame(iframe[0])
                status, statusError = self.getWebElement('XPATH', '//select')
                if status != -1: Select(status[0]).select_by_index(1)
                expression = '//input[contains(@class,"search-text") and contains(@placeholder,"Search")]'
                search, searchError = self.getWebElement('XPATH', expression)
                if search != -1: 
                    code = self.waitWebElement(search[0], expression)
                    if code == 404: search, searchError = self.getWebElement('XPATH', expression)
                    try:
                        search[0].clear()
                        #search[0].send_keys(pixelName+Keys.ENTER)
                        search[0].send_keys(pixelName)
                        self.doWebElement(search[0], 'Enter')
                        pixelTable, pixelTableError = self.getWebElement('XPATH', '//tbody/tr')
                        if pixelTable != -1:
                            pixels, pixelsError = self.getWebElement('XPATH', '//tbody/tr/td[@data-col-name="conversion_name"]')
                            if pixels == -1: (pixels, pixelsError) = self.getWebElement('XPATH', '//tbody/tr/td[@data-col-name="conversion_name"]')
                            if pixels != -1:
                                for pixel in pixels:
                                    if pixelName == pixel.text:
                                        self.driver.switch_to.default_content()
                                        return True
                                else:
                                    self.driver.switch_to.default_content()
                                    return False
                            else:
                                self.driver.switch_to.default_content()
                                return False
                        else:
                            self.driver.switch_to.default_content()
                            return False
                    except:
                        print('Te pille!')
                        self.driver.switch_to.default_content()
                        return False
                else:
                    self.driver.switch_to.default_content()
                    return False
        elif platform == 'Xandr Seg' or platform == 'Xandr Conv':
            query = 'advertiser_id=%s' % advertiserId
            if platform == 'Xandr Seg':
                self.setDriver(urlparse('https://invest.xandr.com/dmp/segments/')._replace(query=query).geturl())
                WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//input[contains(@placeholder,"Search Name or ID")]'))).send_keys(pixelName+Keys.ENTER)
                try:
                    WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.XPATH,'//header[contains(text(),"No Segments Found")]')))
                    return False
                except:
                    segments = WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//div[contains(@class,"dmp-Segments-Segment-Name")]')))
                    for segment in segments:
                        if pixelName == segment.text:
                            return True
                    else:
                        return False
            else:
                query = 'id=%s' % advertiserId
                self.setDriver(urlparse('https://invest.xandr.com/pixel')._replace(query=query).geturl())
                try:
                    WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//header[contains(text(),"No Items Found")]')))
                    return False
                except:
                    WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//span[text()="10"]'))).click()
                    WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//div[text()="100"]'))).click()
                    heads = WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//span[contains(@class,"invest-TruncatedColumn-truncate")]')))
                    for head in heads:
                        pixel = head.find_element(By.XPATH, '..').text.replace('\n','')#Revisar posible problema en esta sentencia
                        if pixel == pixelName:
                            return True
                    else:
                        return False 
        elif platform == 'DV360':
            marketId = self.getDV360MarketId(advertiserId)
            if marketId == -1:
                return False
            else:
                return self.existFloodlight_(pixelName, marketId, advertiserId, 10)
        elif platform == 'Minsights':
            fragment = 'client/%s/activities' % advertiserId
            self.setDriver(urlparse('https://amerminsights.mplatform.com/')._replace(fragment=fragment).geturl())
            iframe = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//div/iframe[contains(@class,"external-iframe")]')))
            self.driver.switch_to.frame(iframe)
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//input[contains(@placeholder,"Search...")]'))).send_keys(pixelName+Keys.ENTER)
            try:
                WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//td[contains(text(),"No results found")]')))
                pixelId = urlparse(self.driver.current_url).path.split('/')[-1]
                return False
            except:
                activities = WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//tbody/tr/td/div/a')))         
                for activity in activities:
                    if activity.text == pixelName:
                        return True
                else:
                    return False
                            
    def existTaboolaPixel(self, advertiserId):
        query = 'accountId=%s' % advertiserId
        self.setDriver(urlparse('https://ads.taboola.com/conversions')._replace(query=query).geturl())
        iframe, iframeError = self.getWebElement('XPATH', '//div/iframe[contains(@title,"Tracking")]')
        if iframe != -1:
            self.driver.switch_to.frame(iframe[0])
            uPixel, uPixelError = self.getWebElement('XPATH','//span[contains(text(),"Pixel Is Active")]')
            if uPixel != -1:
                self.driver.switch_to.default_content()
                return True
            else:
                self.driver.switch_to.default_content()
                return False
        else: 
            return False
    
    def existFloodlight(self, floodName, marketId, advertiserId, timeWait):
        fragment = 'ng_nav/p/%s/a/%s/fl/events'%(marketId,advertiserId)
        self.setDriver(urlparse(self.driver.current_url)._replace(fragment=fragment).geturl())
        time.sleep(timeWait)
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//material-button[contains(@aria-label,"Remove all filters")]')))[0].click()
            time.sleep(10)
        except:
            pass
        try:
            floods = WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//div/ess-cell/name-id-cell/a')))
        except:
            floods = []
        if len(floods)>0:
            for flood in floods:
                if flood.get_attribute('textContent') == floodName:
                    return True
            else:
                return False
        else:
            return False
        
    def existFloodlight_(self, floodName, marketId, advertiserId, timeWait):
        fragment = 'ng_nav/p/%s/a/%s/fl/events'%(marketId,advertiserId)
        self.setDriver(urlparse(self.driver.current_url)._replace(fragment=fragment).geturl())
        webElement, error = self.getWebElement('XPATH','//material-button[contains(@aria-label,"Remove all filters")]', timeout_=1)
        if webElement != -1: webElement[0].click()
        stop = 0
        while stop<3:
            floods, error = self.getWebElement('XPATH','//div/ess-cell/name-id-cell/a')
            if floods == -1:
                stop += 1
            else:
                time.sleep(timeWait)
                webElement, error = self.getWebElement('XPATH','//div[contains(text(),"Show rows:")]', timeout_=1)
                if webElement != 1: self.driver.execute_script("arguments[0].scrollIntoView();", webElement[0])
                time.sleep(2)  
                floods2, error = self.getWebElement('XPATH','//div/ess-cell/name-id-cell/a')
                if len(floods2) > len(floods):
                    floods = floods2
                    stop = 3
                else:
                    stop += 1
        floods = [] if floods==-1 else floods 
        print(len(floods))
        if len(floods)>0:
            for flood in floods:
                if flood.get_attribute('textContent') == floodName:
                    return True
            else:
                print('Caso -2')
                return False
        else:
            print('Caso -1')
            return False
        
    def tearDown(self):
        if not self.driver == None:
            self.driver.quit()

if __name__ == '__main__':
    bot = pixelBot()