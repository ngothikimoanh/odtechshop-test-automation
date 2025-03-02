from selenium import webdriver
from selenium.webdriver.firefox.service import Service

website = "http://localhost/auth/register"


service=Service("geckodriver.exe")
driver = webdriver.Firefox(service=service)

driver.get(website)


