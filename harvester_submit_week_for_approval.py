#!/usr/bin/env python

import argparse
from datetime import datetime, timedelta
import subprocess

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait


def login(driver, wait, email, password):
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

def submit_week_for_approval(driver, wait, subdomain):
    friday = most_recent_friday()

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
    wait.until(expected.visibility_of_element_located(
        (
            By.XPATH,
            '//a[@aria-label="{}"]'.format(friday.strftime('%A, %d %B'))
        )))

    approval_button = driver.find_element_by_css_selector(
        '.approval-button .submit-link')

    # Don't submit if the time sheet has already been submitted
    if approval_button.text == 'Resubmit Week for Approval':
        return driver

    # Click "Submit Week for Approval" button
    approval_button.click()

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

def get_password(command):
    result = subprocess.run(['sh', '-c', command], stdout=subprocess.PIPE)

    return str(result.stdout, 'utf-8').rstrip()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Submit the most recent Harvest timesheet for approval.')
    parser.add_argument(
        '--email',
        required=True,
        help='Harvest email address')
    parser.add_argument(
        '--password-command',
        required=True,
        help='Shell command to get Harvest password')
    parser.add_argument(
        '--subdomain',
        required=True,
        help='Harvest subdomain (acme in acme.harvestapp.com)')

    args = parser.parse_args()

    options = Options()
    options.add_argument('-headless')
    driver = Firefox(
        executable_path='./geckodriver',
        firefox_binary='/Applications/FirefoxDeveloperEdition.app/Contents/MacOS/firefox-bin',
        firefox_options=options)

    wait = WebDriverWait(driver, timeout=10)

    driver = login(
        driver,
        wait,
        args.email,
        get_password(args.password_command))
    driver = submit_week_for_approval(driver, wait, args.subdomain)

    driver.quit()
