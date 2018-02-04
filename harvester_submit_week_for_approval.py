#!/usr/bin/env python

import argparse
from datetime import datetime, timedelta
import subprocess
import sys

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait

import requests


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
        print('Week was already submitted', file=sys.stderr)

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


class WeekIsComplete(object):

    def __init__(self, account_id, api_token, friday):
        self.account_id = account_id
        self.api_token = api_token
        self.friday = friday
        self._monday = None
        self.days = {}

        # Add `self.days['2018-01-31'] = 0` for all weekdays
        for i in range(5):
            self.days[(self.monday + timedelta(days=i)).strftime('%F')] = 0

    def check(self):
        time_entries = self._fetch_week()
        days = self.days.keys()

        for entry in time_entries['time_entries']:
            if entry['spent_date'] in days:
                self.days[entry['spent_date']] += 1

        for _, count in self.days.items():
            if count == 0:
                raise IncompleteWeekError

        return True

    def _fetch_week(self):
        r = requests.get(
            'https://api.harvestapp.com/api/v2/time_entries',
            headers={
                'Harvest-Account-ID': self.account_id,
                'Authorization': 'Bearer {}'.format(self.api_token),
                'User-Agent': 'harvester-submit-week-for-approval (TODO email address or link to app)',
                'Content-Type': 'application/json',
            },
            params={
                'from': self.monday.strftime('%F'),
                'to': self.friday.strftime('%F'),
            })

        return r.json()

    @property
    def monday(self):
        if not self._monday:
            self._monday = self.friday - timedelta(days=4)

        return self._monday


class IncompleteWeekError(RuntimeError):
    pass


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
    parser.add_argument(
        '--account-id',
        required=True,
        help='Harvest account ID')
    parser.add_argument(
        '--api-token',
        required=True,
        help='Harvest API token (https://id.getharvest.com/developers)')

    args = parser.parse_args()

    # Don't submit unless there is at least 1 time sheet logged for each day
    # that week
    try:
        WeekIsComplete(
            account_id=args.account_id,
            api_token=args.api_token,
            friday=most_recent_friday()
        ).check()
    except IncompleteWeekError:
        print('Week was incomplete', file=sys.stderr)

        sys.exit(1)

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
