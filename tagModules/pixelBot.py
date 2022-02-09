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
                        return True, ID.query
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
            print('Verificación Login Page de manera larga')
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
        elif self.isVerifyPage():
            print('It is verify page!!!')
            e,  verify = self.existWebElement('verify')
            e_, code   = self.existWebElement('code', time_=0)
            if e:
                verify.click()
            else:
                self.reqCode = True
                if not self.code == None:
                    code.send_keys(self.code+Keys.ENTER)
                    self.reqCode = False
                    self.code = None
        elif self.driver.title == 'Hello':
            try:
                self.driver.find_element(By.PARTIAL_LINK_TEXT,'Taboola Ads').click()
            except Exception:
                self.authFail = True
        else:
            if self.startLog:
                return True
            else:
                return False
        return False
    
    def auth_alert(self, time_=1):
        try:
            alert = WebDriverWait(self.driver, time_).until(EC.visibility_of_any_elements_located((By.XPATH, "//input[contains(@class,'error')]|//input[@aria-invalid='true']|//div[contains(@class,'error')]|//*[contains(text(),'No tenemos noticias') or contains(text(),'denegada') or contains(text(),'hear from you') or contains(text(),'denied')]")))
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
            snipet_pixel = """<!-- Segment Pixel - %s - DO NOT MODIFY -->
                            <script src="https://secure.adnxs.com/seg?add=%s&t=1" type="text/javascript"></script>
                            <!-- End of Segment Pixel -->"""%(pixelName, pixelId)   
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
            snipet_pixel = """<!-- Conversion Pixel - %s - DO NOT MODIFY -->
                            <script src="https://secure.adnxs.com/px?id=%s&t=1" type="text/javascript"></script>
                            <!-- End of Conversion Pixel -->"""%(pixelName, pixelId)   
            return  snipet_pixel
        elif platform == 1:
            pass
        elif platform == 2:
            pass
        elif platform == 3:
            pass

    def tearDown(self):
        if not self.driver == None:
            self.driver.quit()

if __name__ == '__main__':
    bot = pixelBot()
