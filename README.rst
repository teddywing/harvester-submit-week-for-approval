Harvester Submit Week For Approval
==================================

This program will automatically submit this week’s time sheet for approval. It
is intended to be run automatically by ``launchd`` or ``cron``. The time sheet
will only be submitted if at least one time entry has been added for every
weekday in the week.

By automating time sheet submission, the program frees human time loggers from
having to remember or worry about doing so.

This script is implemented with Selenium using Firefox’s headless mode (or
another browser, if you prefer). At the time of implementation, no API exists to
submit time sheets for approval, and authenticity tokens made it difficult to
use regular HTTP requests, leaving Selenium the only remaining option.


Install
-------

1. Clone the repository
2. Install dependencies::

    $ pipenv install

3. (OS X only) Modify the
   ``com.teddywing.harvester-submit-week-for-approval.plist`` file:

   a. Change the executable path to the virtualenv’s ``python3``
   b. Use the absolute path to ``harvester_submit_week_for_approval.py``
   c. Fill in your Harvest account details. A developer token can be obtained
      at https://id.getharvest.com/developers.
   d. Put the plist in ``~/Library/LaunchAgents/``
   e. Load the plist with::

       launchctl load /path/to/com.teddywing.harvester-submit-week-for-approval.plist

4. Download `geckodriver`_

   a. Replace the ``geckodriver`` path on `this line`_ with the absolute path
      to the executable on your machine.


License
-------

Copyright © 2018 Teddy Wing. Licensed under the GNU GPLv3+ (see the included
COPYING file).


.. _geckodriver: https://github.com/mozilla/geckodriver/releases
.. _this line: https://github.com/teddywing/harvester-submit-week-for-approval/blob/faa4d4c0831b70b5e103d0337c816db025ef8a9f/harvester_submit_week_for_approval.py#L209
