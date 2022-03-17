from urllib.parse import urlparse
import requests
import time
import re

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from selenium.common.exceptions import StaleElementReferenceException

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

class pixelBot:
    def __init__(self):
        self.driver   = None
        self.url      = None
        self.authFail = False
        self.set      = True
        self.reqCode  = False
        self.verifyWE = None
        self.codeWE   = None
        self.emailWE  = None
        self.passwdWE = None
        self.submitWE = None
        self.startLog = False
        self.code     = None
        self.approve  = False

    def setUrl(self, url):
        self.url = url

    def setDriver(self, url):
        if self.set:
            self.driver = self.setHeadlessMode()
            self.set    = False
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
                print('It is verify page!!!')
                return True
        else:
            exist,  h = self.existWebElement('verify', time_=5)
            exist_, h = self.existWebElement('code', time_=0)
            if exist or exist_:
                print('It is verify page!!!')
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
        elif self.isVerifyPage():
            e,  verify = self.existWebElement('verify')
            e_, code   = self.existWebElement('code', time_=0)
            if e:
                verify.click()
                print('It is verify page!!!')
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
                
    def createPixel(self, advertiserId, pixelName, platform=0, pixelType='RTG'):
        if platform == 0 and pixelType=='RTG':
            query = 'advertiser_id=%s' % advertiserId
            self.setDriver(urlparse('https://invest.xandr.com/dmp/segments/new')._replace(query=query).geturl())
            WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[@placeholder="Enter a segment name"]')))[0].send_keys(pixelName)
            WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,'//button/span[contains(text(),"Save")]')))[0].click()
            time.sleep(5)
            pixelId = urlparse(self.driver.current_url).path.split('/')[-1]
            snipet_pixel = """<!-- Segment Pixel - %s - DO NOT MODIFY -->\n<script src="https://secure.adnxs.com/seg?add=%s&t=1" type="text/javascript"></script>\n<!-- End of Segment Pixel -->"""%(pixelName, pixelId)   
            return  snipet_pixel
        elif platform == 0 and pixelType=='CONV':
            query = 'id=%s' % advertiserId
            self.setDriver(urlparse('https://invest.xandr.com/pixel')._replace(query=query).geturl())
            WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,'//button/span[contains(text(),"New")]')))[0].click()
            WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@class,"PixelModal-name")]')))[0].send_keys(pixelName)
            WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,'//span[contains(text(),"Select...") or contains(text(),"View an item") or contains(text(),"Add to cart") or contains(text(),"Initiate checkout") or contains(text(),"Add payment info") or contains(text(),"Purchase") or contains(text(),"Generate lead")]')))[0].click()
            WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,'//div[contains(text(),"Generate lead")]')))[0].click()
            WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,'//div[contains(text(),"Count all conversions per user")]')))[0].click()
            WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,'//button/span[contains(text(),"Save")]')))[0].click()
            new_query = '//span[contains(@title,"%s")]'%pixelName
            pixelId = re.findall(r'-?\d+\.?\d*', WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH,new_query)))[0].get_attribute('title'))[0]
            snipet_pixel = """<!-- Conversion Pixel - %s - DO NOT MODIFY -->\n<script src="https://secure.adnxs.com/px?id=%s&t=1" type="text/javascript"></script>\n<!-- End of Conversion Pixel -->"""%(pixelName, pixelId)   
            return  snipet_pixel
        elif platform == 1:
            self.setDriver('https://displayvideo.google.com/')
            #self.driver.find_elements(By.XPATH,'//material-button[contains(@class,"search")]')[0].click()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//material-button[contains(@class,"search _ngcontent")]')))[0].click()
            search = WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@placeholder,"Search by name or ID")]')))[0]
            preURL = self.driver.current_url
            search.send_keys(advertiserId)
            #box = self.driver.find_elements(By.XPATH,'//input[contains(@placeholder,"Search by name or ID")]')[0]
            time.sleep(2)
            search.send_keys(Keys.ENTER)
            print('iniciamos espera')
            time.sleep(10)
            if self.driver.current_url == preURL:
                print(self.driver.current_url)
                return "The Advertiser with ID %s, there isn't be!" % advertiserId
            marketId, h = re.findall(r'-?\d+\.?\d*',self.driver.current_url)
            # Details set up
            if self.existFloodlight(pixelName, marketId, advertiserId, 10): return "This Floodlight name there be exist yet!"
            fragment = 'ng_nav/p/%s/a/%s/fl/details'%(marketId,advertiserId)
            self.setDriver(urlparse(self.driver.current_url)._replace(fragment=fragment).geturl())
            # Process
            # Create floodlight: Valid last url in the basis details process
            try:
                variables = WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//span[starts-with(text(),"u") and (contains(text(),": u") or contains(text(),": p"))]')))
                WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-icon[@id="open-custom-variables-icon"]')))[0].click()
                existU, indexU = self.existVariable('u', 'div')
                existP, indexP = self.existVariable('p', 'div')
                print('Existe U: ',existU)
                print('Existe P: ',existP)
                if existU==False and existP==False:
                    self.createCustomVariable('u')
                    time.sleep(10)
                    WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-icon[@id="open-custom-variables-icon"]')))[0].click()
                    self.createCustomVariable('p')
                elif existU==False:
                    self.createCustomVariable('u')
                elif existP==False:
                    self.createCustomVariable('p')
                else:
                    WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-button[contains(@id,"save-button")]')))[1].click()
            except:
                WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-icon[@id="open-custom-variables-icon"]')))[0].click()
                self.createCustomVariable('u')
                print('Primera Espera')
                time.sleep(10)
                print('Termina Espera')
                WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-icon[@id="open-custom-variables-icon"]')))[0].click()
                self.createCustomVariable('p')
                #WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-button[contains(@class,"green")]')))[0].click()
                #WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-button[contains(@class,"green")]')))     
            fragment = 'ng_nav/p/%s/a/%s/fl/events/new'%(marketId,advertiserId)
            self.setDriver(urlparse(self.driver.current_url)._replace(fragment=fragment).geturl())
            # Process 
            WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH, '//div[contains(@id,"entity-type-card-activityWeb")]')))[0].click()
            WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH, '//input[contains(@debugid,"acx_177925851_179054344")]')))[0].send_keys(pixelName)
            WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH, '//div[contains(text(),"Image tag")]')))[0].click()
            WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH, '//div[contains(text(),"Counter")]')))[0].click()
            WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH, '//div[contains(text(),"Standard")]')))[0].click()
            WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH, '//div[contains(text(),"exclude")]')))[0].click()
            WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.XPATH, '//div[contains(text(),"Enable this Display & Video 360 activity for remarketing.")]')))[0].click()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-icon[@id="open-custom-variables-icon"]')))[0].click()
            existU, indexU = self.existVariable('u')
            existP, indexP = self.existVariable('p')
            custom_check = WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//picker-tree/div/material-checkbox')))
            custom_check[indexU].click()
            custom_check[indexP].click()

            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-button[contains(@id,"save-button")]')))[1].click()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-button[contains(@id,"save-button")]')))[0].click()
            time.sleep(10)
            marketId, advertiserId, floodlightId = re.findall(r'-?\d+\.?\d*',self.driver.current_url)
            fragment = 'ng_nav/p/%s/a/%s/fl/fle/%s/code'%(marketId,advertiserId,floodlightId)
            self.setDriver(urlparse(self.driver.current_url)._replace(fragment=fragment).geturl())
            time.sleep(10)
            snipet_pixel = self.driver.find_elements(By.XPATH,'//div[contains(@class,"mirror-text") and contains(@class,"_ngcontent")]')[0].get_attribute('textContent')
            return  snipet_pixel
        elif platform == 2 and pixelType=='RTG':
            query = 'accountId=%s' % advertiserId
            self.setDriver(urlparse('https://ads.taboola.com/audiences/pixel-based/new')._replace(query=query).geturl())
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//div[@id="name"]')))[0].send_keys(pixelName)
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH,'//input[contains(@placeholder,"URL Address")]'))).send_keys('/test')
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH,'//button/span[contains(text(),"ADD")]'))).click()
            #WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//button/span[contains(text(),"Create Audience")]')))[0].click()
            return 'Test_Taboola'
        elif platform == 2 and pixelType=='CONV':
            query = 'accountId=%s' % advertiserId
            self.setDriver(urlparse('https://ads.taboola.com/conversions')._replace(query=query).geturl())
            print('Se ha cargado la primera pagina')
            time.sleep(10)
            iframe = WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//div/iframe[contains(@title,"Tracking")]')))
            print(type(iframe))
            self.driver.switch_to.frame(iframe[0])
            time.sleep(5)
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//a[@id="btn-new-rule"]')))[0].click()
            time.sleep(10)
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//button[contains(text(),"Event")]')))[0].click()
            print('Hemos seleccionado event????')
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//button[contains(text(),"Custom")]')))[0].click()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[@id="conversionName"]')))[0].send_keys(pixelName)
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[@id="eventName"]')))[0].send_keys(pixelName)
            Select(self.driver.find_element(By.XPATH,'//select[contains(@id,"conversionCategory")]')).select_by_index(8)
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//button[@data-name="excludeFromCampaigns"]')))[0].click()
            snippet = self.driver.find_element(By.XPATH,'//textarea[@id="codeSnippet"]')
            self.driver.switch_to.default_content()
            return snippet
        elif platform == 3:
            fragment = 'client/%s/activities' % advertiserId
            self.setDriver(urlparse('https://amerminsights.mplatform.com')._replace(fragment=fragment).geturl())
            iframe = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//div/iframe[contains(@class,"external-iframe")]')))
            self.driver.switch_to.frame(iframe)
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//button[contains(@id,"createButton") and contains(text(),"Create Activity")]'))).click()
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//input[@id="name"]'))).send_keys(pixelName)
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//span[contains(text(),"for Consumer Correlation")]'))).click()
            WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"customvariable_")]')))[0].send_keys('p')
            WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"variableId")]')))[0].send_keys('p')
            WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//a[contains(text(),"add")]')))[0].click()
            WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"customvariable_")]')))[1].send_keys('p')
            WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"variableId")]')))[1].send_keys('u')
            WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//a[contains(text(),"add")]')))[0].click()
            #WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//div[contains(text(),"SAVE")]'))).click()
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//input[contains(@placeholder,"Search...")]'))).send_keys(pixelName+Keys.ENTER)
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//i[@class="js-activity-tag turbine tag link icon"]'))).click()
            snippet = WebDriverWait(bot.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//textarea[@id="activityTagCode"]'))).get_attribute('value')
            self.driver.switch_to.default_content()
            return snippet
        
    def createCustomVariable(self, variable):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-button[contains(@debugid,"creation-button") or contains(text(),"ADD CUSTOM")]')))[0].click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//div[contains(@class,"particle-table-last-row")]')))[0].click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//*[contains(@aria-label,"Edit this Name")]')))[0].click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//input')))[-1].send_keys(variable)
        WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-button[contains(@class,"btn-yes")]')))[0].click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-button[contains(@id,"save-button")]')))[1].click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, '//material-button[contains(@id,"save-button")]')))[0].click()

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
            
    def existAdvertiserId(self, platform_, advertiserId):
        #['Xandr Seg', 'Xandr Conv', 'DV360', 'Taboola', 'minsights']
        if platform_ == 'Xandr Seg' or platform_ == 'Xandr Conv':
            try:
                self.setDriver('https://invest.xandr.com/bmw/advertisers')
                time.sleep(10)
                #search = WebDriverWait(bot.driver,10).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@placeholder,"Search")]')))
                search = self.driver.find_elements(By.XPATH,'//input[@placeholder="Search"]')
                len(search)
                search[0].clear()
                search[0].send_keys(advertiserId+Keys.ENTER)
                try:
                    WebDriverWait(bot.driver,10).until(EC.visibility_of_any_elements_located((By.XPATH,'//div/header[contains(text(),"No Data")]')))
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
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//div[contains(@class,"accountPicker_container__1sNyQ")]')))[0].click()
            time.sleep(5)
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"react-select-")]')))[0].clear()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"react-select-")]')))[0].send_keys(advertiserId)
            time.sleep(2)
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"react-select-")]')))[0].send_keys(Keys.ENTER)
            time.sleep(3)
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
    
    """
        This method implement a function to search the advertiser in Minsights Platform.
        Return:
            AdvertiserId: String or -1 if the advertiserName there's not exist.     
    """         
    def existMinsightsId(self, advertiserName, advertiserCountry):
        #self.driver.switch_to.default_content()
        #self.setDriver('https://amerminsights.mplatform.com/')
        #WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//i')))[1].click()
        #WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@placeholder,"Search")]')))[0].clear()
        #WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@placeholder,"Search")]')))[0].send_keys(advertiserCountry)
        #WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@placeholder,"Search")]')))[0].send_keys(Keys.ENTER)
        self.setMinsightsCountry(advertiserCountry)
        self.setDriver('https://amerminsights.mplatform.com/#client')
        self.driver.switch_to.default_content()
        iframe = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//div/iframe[contains(@class,"external-iframe")]')))
        self.driver.switch_to.frame(iframe)
        try:
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//input[contains(@placeholder,"Search...")]'))).send_keys(advertiserName+Keys.ENTER)
        except:
            bot.driver.switch_to.default_content()
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
        
    def existPixel(self, platform, advertiserId, pixelName):
        if platform == 'Taboola Seg' or platform == 'Taboola Conv':
            query = 'accountId=%s' % advertiserId
            if platform == 'Taboola Seg':
                query = query + '&reportId=pixel-based'
                self.setDriver(urlparse('https://ads.taboola.com/audiences')._replace(query=query).geturl())
                WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//button[contains(@aria-label,"Remove audienceStatus filter")]')))[0].click()
                WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[contains(@id,"grid-quick-filter")]')))[0].send_keys(pixelName+Keys.ENTER)
                try:
                    WebDriverWait(bot.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//span[contains(text(),"No available data for this selection")]')))
                    return False
                except:
                    pixels = WebDriverWait(bot.driver, 120).until(EC.visibility_of_any_elements_located((By.XPATH,'//div[@col-id="pixel-based_audienceName"]')))
                    for pixel in pixels:
                        print(pixel.text)
                        if pixelName == pixel.text:
                            return True
                    else:
                        return False
            else:
                self.setDriver(urlparse('https://ads.taboola.com/conversions')._replace(query=query).geturl())
                iframe = WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//div/iframe[contains(@title,"Tracking")]')))
                self.driver.switch_to.frame(iframe[0])
                Select(WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//select')))).select_by_index(1)
                print('Empieza la espera')
                time.sleep(30)
                #Select(self.driver.find_element(By.XPATH,'//select')).select_by_index(1)
                WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//input[contains(@class,"search-text") and contains(@placeholder,"Search")]'))).clear()
                WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//input[contains(@class,"search-text") and contains(@placeholder,"Search")]'))).send_keys(pixelName+Keys.ENTER)
                
                try:
                    WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.XPATH,'//tbody/tr')))
                    try:
                        pixels = WebDriverWait(self.driver, 120).until(EC.visibility_of_any_elements_located((By.XPATH,'//tbody/tr/td[@data-col-name="conversion_name"]')))
                    except:
                        pixels = self.driver.find_elements(By.XPATH,'//tbody/tr/td[@data-col-name="conversion_name"]')
                    for pixel in pixels:
                        print(pixel.text)
                        if pixelName == pixel.text:
                            self.driver.switch_to.default_content()
                            return True
                    else:
                        self.driver.switch_to.default_content()
                        return False
                except:
                    self.driver.switch_to.default_content()
                    return False
        elif platform == 'Xandr Seg' or platform == 'Xandr Conv':
            query = 'advertiser_id=%s' % advertiserId
            if platform == 'Xandr Seg':
                self.setDriver(urlparse('https://invest.xandr.com/dmp/segments/')._replace(query=query).geturl())
                WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//input[contains(@placeholder,"Search Name or ID")]'))).send_keys(pixelName+Keys.ENTER)
                try:
                    WebDriverWait(self.driver, 240).until(EC.visibility_of_element_located((By.XPATH,'//header[contains(text(),"No Segments Found")]')))
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
                        print(pixel)
                        if pixel == pixelName:
                            return True
                    else:
                        return False 
        elif platform == 'Minsights':
            fragment = 'client/%s/activities' % advertiserId
            self.setDriver(urlparse('https://amerminsights.mplatform.com/')._replace(fragment=fragment).geturl())
            iframe = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//div/iframe[contains(@class,"external-iframe")]')))
            self.driver.switch_to.frame(iframe)
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//input[contains(@placeholder,"Search...")]'))).send_keys(pixelName+Keys.ENTER)
            try:
                WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH,'//td[contains(text(),"No results found")]')))
                return False
            except:
                activities = WebDriverWait(self.driver, 30).until(EC.visibility_of_any_elements_located((By.XPATH,'//tbody/tr/td/div/a')))         
                for activity in activities:
                    if activity.text == pixelName:
                        return True
                else:
                    return False
                            
    def existFloodlight(self, floodName, marketId, advertiserId, timeWait):
        fragment = 'ng_nav/p/%s/a/%s/fl/events'%(marketId,advertiserId)
        self.setDriver(urlparse(self.driver.current_url)._replace(fragment=fragment).geturl())
        time.sleep(timeWait)
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH,'//material-button[contains(@aria-label,"Remove all filters")]')))[0].click()
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
        
    def tearDown(self):
        if not self.driver == None:
            self.driver.quit()

if __name__ == '__main__':
    bot = pixelBot()
