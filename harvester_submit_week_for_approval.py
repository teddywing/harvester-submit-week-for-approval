#!/usr/bin/env python

from datetime import datetime, timedelta

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait

email = ''
password = ''
subdomain = ''


def login(driver, wait):
    driver.get('https://id.getharvest.com/harvest/sign_in')

    wait.until(
        expected.visibility_of_element_located((By.NAME, 'email'))
    ).send_keys(email)
    driver.find_element_by_name('password').send_keys(password + Keys.ENTER)

    wait.until(
        expected.visibility_of_element_located((By.ID, 'user-dropdown-toggle'))
    )

    return driver

def most_recent_friday():
    friday = 4
    now = datetime.now()

    if now.weekday() >= friday:
        return now - timedelta(days=now.weekday() - friday)
    else:
        return now - timedelta(weeks=1) + timedelta(days=friday - now.weekday())

def submit_week_for_approval(driver, wait):
    # friday = most_recent_friday()
    friday = datetime(2018, 1, 15)

    url = 'https://{subdomain}.harvestapp.com/time/week/{year}/{month}/{day}/'.format(
        subdomain=subdomain,
        year=friday.year,
        month=friday.month,
        day=friday.day)

    driver.get(url)

    # Wait for page to load
    wait.until(expected.text_to_be_present_in_element(
        (By.CLASS_NAME, 'timesheet-header'),
        str(friday.year)))
    wait.until(expected.text_to_be_present_in_element(
        (By.CSS_SELECTOR, '.day .js-day'),
        friday.strftime('%d %b')))

    # Click "Submit Week for Approval" button
    driver.find_element_by_css_selector(
        '.approval-button .submit-link'
    ).click()

    # Click "Yes, Submit Timesheet" button
    wait.until(
        expected.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                '.approval-confirmation .js-submit-for-approval',
            )
        )
    ).click()

    # Wait for success message
    wait.until(expected.text_to_be_present_in_element(
        (By.ID, 'status_message'),
        'Timesheet has been submitted for approval.'))

    return driver

if __name__ == "__main__":
    options = Options()
    # options.add_argument('-headless')
    driver = Firefox(
        executable_path='./geckodriver',
        firefox_binary='/Applications/FirefoxDeveloperEdition.app/Contents/MacOS/firefox-bin',
        firefox_options=options)

    wait = WebDriverWait(driver, timeout=10)

    driver = login(driver, wait)
    driver = submit_week_for_approval(driver, wait)

    print(driver.page_source)

    # import time; time.sleep(20)
    driver.quit()
