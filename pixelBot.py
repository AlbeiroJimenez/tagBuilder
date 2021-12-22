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


if __name__ == '__main__':
    fireFoxOptions = webdriver.FirefoxOptions()
    #fireFoxOptions.headless = True
    #fireFoxOptions.set_preference("general.useragent.override", USER_AGENT)
    fireFoxOptions.page_load_strategy = 'eager'
    browser = webdriver.Firefox(options = fireFoxOptions)