# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 15:29:33 2021

@author: Albeiro.Jimenez
"""

from urllib.parse import urlparse
import requests
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.common.exceptions import StaleElementReferenceException

LOGIN = {
    'sign in', 'acceso: cuentas', 'login', 'log in', 'account', 'iniciar sesión', 'cuenta'
    }

VERIFY = {
    '2nd factor', 'authentication', 'Check Your Email', 'Verification', 'Verify'
    }

fireFoxOptions = webdriver.FirefoxOptions()
fireFoxOptions.page_load_strategy = 'eager'
browser = webdriver.Firefox(options = fireFoxOptions)

def find_input_email():
    pass

def find_input_password():
    pass

def existWebElement(webElement='email'):
    if webElement=='email':
        emails = browser.find_elements(By.XPATH,'//input[@type="email"]|//input[contains(@name,"user")]|//input[contains(@name,"login")]|//input[contains(@name,"session")]')
        for email in emails:
            if not email.is_displayed():
                emails.remove(email)
        if len(emails)>0:
            return True
        else:
            return False       
    elif webElement=='password':
        passwords = browser.find_elements(By.XPATH,'//input[@type="password"]')
        for password in passwords:
            if not password.is_displayed():
                passwords.remove(password)
        if len(passwords)>0:
            return True
        else:
            return False
    elif webElement=='submit':
        buttons = browser.find_elements(By.XPATH,'//button[@type="button"]|//button[@type="submit"]|//input[@type="submit"]|//button[contains(@id,"submit")]')
        for button in buttons:
            if not button.is_displayed():
                buttons.remove(button)
        if len(buttons)>0:
            return True
        else:
            return False
    elif webElement=='verify':
        texts = browser.find_elements(By.XPATH, '//div[contains(text(),"Enviar un mensaje de texto al")]')
        for text in texts:
            if not text.is_displayed():
                texts.remove(text)
        if len(texts)>0:
            return True
        else:
            return False   
    elif webElement=='code':
        codes = browser.find_elements(By.XPATH, '//input[contains(@name,"code")]|//input[contains(@id,"code")]|//input[contains(@placeholder,"code")]|//input[contains(@placeholder,"Código")]')
        for code in codes:
            if not code.is_displayed():
                codes.remove(code)
        if len(codes)>0:
            return True
        else:
            return False  
    else:
        return False
    
def isLoginPage():
    for loginWord in LOGIN:
        if loginWord.casefold() in browser.title.casefold() and not isVerifyPage():
            return True
    else:
        if existWebElement() or existWebElement('password'):
            return True
        else:
            return False
    # We requiere a process to determine if a webpage is a login page throught scraping and crawling.
    #I need to implement verification by structure basic, Login Page: input mail and button submit
    
def isVerifyPage():
    for verify_word in VERIFY:
        if verify_word.casefold() in browser.title.casefold():
            return True
    else:
        if existWebElement('verify') or existWebElement('code'):
            return True
        else:
            return False


if __name__ == '__main__':
    
    #fireFoxOptions.headless = True
    #fireFoxOptions.set_preference("general.useragent.override", USER_AGENT)
    emails = browser.find_elements(By.XPATH,"//input[contains(text(),'user')]")
