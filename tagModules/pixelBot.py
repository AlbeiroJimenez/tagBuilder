from urllib.parse import urlparse
import requests
import time

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
        
    def existWebElement(self, webElement='email'):
        if webElement=='email':
            try:
                #emails = self.driver.find_elements(By.XPATH,'//input[@type="email"]|//input[contains(@name,"user")]|//input[contains(@name,"login")]|//input[contains(@name,"session")]|//input[contains(@name,"email")]')
                emails = WebDriverWait(self.driver, 1).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[@type="email"]|//input[contains(@name,"user")]|//input[contains(@name,"login")]|//input[contains(@name,"session")]|//input[contains(@name,"email")]')))
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
                passwords = WebDriverWait(self.driver, 1).until(EC.visibility_of_any_elements_located((By.XPATH,'//input[@type="password"]')))
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
                buttons = WebDriverWait(self.driver, 1).until(EC.visibility_of_any_elements_located((By.XPATH,'//button[@type="button"]|//button[@type="submit"]|//input[@type="submit"]|//button[contains(@id,"submit")]')))
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
                texts = WebDriverWait(self.driver, 1).until(EC.visibility_of_any_elements_located((By.XPATH, '//div[contains(text(),"Enviar un mensaje de texto al")]')))
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
                codes = WebDriverWait(self.driver, 1).until(EC.visibility_of_any_elements_located((By.XPATH, '//input[contains(@name,"code")]|//input[contains(@id,"code")]|//input[contains(@placeholder,"code")]|//input[contains(@placeholder,"Código")]')))
                for code in codes:
                    if not code.is_displayed():
                        codes.remove(code)
                if len(codes)>0:
                    return True, codes[0]
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
            exist,  h = self.existWebElement()
            exist_, h = self.existWebElement('password')
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
            exist,  h = self.existWebElement('verify')
            exist_, h = self.existWebElement('code')
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
            e_, passwd = self.existWebElement('password')
            if e and e_:
                email.clear()
                passwd.clear()
                email.send_keys(user)
                passwd.send_keys(password+Keys.ENTER)
            elif e:
                email.send_keys(user+Keys.ENTER)
            elif e_:
                passwd.send_keys(password+Keys.ENTER)
            else:
                pass
        elif self.isVerifyPage():
            e,  verify = self.existWebElement('verify')
            e_, code   = self.existWebElement('code')
            if e:
                verify.click()
            else:
                #self.reqCode = True if self.reqCode == False else False
                self.reqCode = True
                if not self.code == None:
                    code.send_keys(self.code+Keys.ENTER)
                    #time.sleep(15)
                    self.reqCode = False
                    self.code = None
                print(self.code)
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
    def auth_alert(self):
        alert = self.driver.find_elements(By.XPATH, "//input[contains(@class,'error')]|//input[@aria-invalid='true']|//div[contains(@class,'error')]")        
        self.deleteItemList(alert, '')
        for alert_ in alert:
            if not alert_.is_displayed():
                alert.remove(alert_)
        if len(alert)>0:
            return True
        else:
            return False

    def deleteItemList(self, list_, item, WE=True):
        if WE:
            for webElement in list_:
                if webElement.get_attribute('textContent') == item:
                    list_.remove(webElement)
        else:
            for i in range(list_.count(item)):
                list_.pop(list_.index(item))

    def tearDown(self):
        if not self.driver == None:
            self.driver.quit()

if __name__ == '__main__':
    bot = pixelBot()
