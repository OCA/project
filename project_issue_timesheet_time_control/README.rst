.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

====================================
Project Issue Timesheet Time Control
====================================

This module adds a button at project issue timesheets to compute the spent
time, in minutes, from start date to the current moment.

It also allows to open and close issues from account analytic lines.
The selected closed stage is the first one that is found with the mark "Closed"
checked.

Installation
============

This module is auto-installed when you install
*project_timesheet_time_control* and *project_issue_sheet*.

Usage
=====

You can access via timesheets:

#. Go to Timesheets > My Timesheets > Detailed Activities.
#. Create a new record.
#. If you don't select any "Project", you will be able to select any "Issue",
   opened or not.
#. Selecting an "Issue", the corresponding "Project" is filled.
#. Selecting a "Project", "Issues" are filtered for only allowing
   to select opened issues for that project. Remember that an opened issue is
   an issue whose stage doesn't have "Closed" mark checked.
#. At the end of the line, you will see an stop icon.
#. When you press this button, the difference between "Date" field and the
   current time, writing this in the field "Duration".
#. You can modify the "Date" field for altering the computation of the
   duration.

or via issues:

#. Go to Project > Search > Issues.
#. Click on one existing issue or create a new one.
#. On the "Timesheets" page, you will be able to handle records the same way
   as you do in the above explanation (except the issue selection part, which
   in this case doesn't appear as it's the current one).

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/project/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback `here <https://github.com/OCA/project/issues/new>`_.

Credits
=======

Contributors
------------
* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Luis M. ontalba <luis.martinez@tecnativa.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
