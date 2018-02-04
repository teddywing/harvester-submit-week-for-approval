#!/usr/bin/env python

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait

email = ''
password = ''
subdomain = ''

def login(driver):
    wait = WebDriverWait(driver, timeout=10)

    driver.get('https://id.getharvest.com/harvest/sign_in')

    wait.until(
        expected.visibility_of_element_located((By.NAME, 'email'))
    ).send_keys(email)
    driver.find_element_by_name('password').send_keys(password + Keys.ENTER)

    return driver

if __name__ == "__main__":
    options = Options()
    # options.add_argument('-headless')
    driver = Firefox(
        executable_path='./geckodriver',
        firefox_binary='/Applications/FirefoxDeveloperEdition.app/Contents/MacOS/firefox-bin',
        firefox_options=options)

    driver = login(driver)

    print(driver.page_source)

    import time; time.sleep(20)
    driver.quit()
