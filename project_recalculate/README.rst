.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3
    :target: http://www.gnu.org/licenses/agpl.html

===================
Project Recalculate
===================

This module recalculates Task start/end dates depending on Project
start/end dates.

Configuration
=============

You can define working calendar at Setting > Technical > Resource > Working time
Then assign this calendar to a resource (related with an user), a project or
a company

When calculating task dates, this addon will look for a working calendar in this order:

* If project has working time assigned, use it.
* If user assigned, search first resource related with this user
  (normally user is related, only with one resource) and get its working calendar
  ends at 18:00
* If not user assigned or resource hasn't working calendar, search first
  working calendar of the company
* If no working calendar found, then every day is workable and work starts at
  08:00 and ends at 18:00

Also you can define which task stages are included in recalculation when
'Project recalculate' button is clicked. By default, all are included.
To change this go to Project > Configuration > Stages > Task Stages and change
'Include in project recalculate' field


Usage
=====

There are two calculation modes:

* **Date begin**: Task start/end dates are recalculated from project's date begin
* **Date end**: Task start/end dates are recalculated from project's date end

If the project start/end date is changed in the form view, then you have to
click "Recalculate project" button to recalculate all open tasks [1]
according to the new date.

[1] 'Open tasks' means tasks in a stage that are defined with
'Include in project recalculate' = True

This a typical use case:

#. Create a project and configure:
    * Calculation type, for example "Date end".
    * Expiration Date.
#. Create tasks, configuring for each one:
    * From days, in this example, days from date end when this task must start.
    * Estimation days, duration of the task in days.
#. Click at "Recalculate project" button.
#. Go to task list and see the recalculated planning.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/10.0


Known issues / Roadmap
======================

* Project tasks are written one by one, so this can reduce performance.


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

* Endika Iglesias
* Rafael Blasco <rafael.blasco@tecnativa.com>
* Antonio Espinosa
* Javier Iniesta
* Pedro M. Baeza <pedro.baeza@tecnativa.com>

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
