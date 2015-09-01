.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

===================
Project Recalculate
===================

This module recalculates Task start/end dates depending on Project
start/end dates.


Instalation
===========

This addon requires Odoo v8 after 2015-08-24 because is not fully functional
without this patch: `Odoo PR #8208 <https://github.com/odoo/odoo/pull/8208>`


Configuration
=============

You can define working calendar at Setting > Technical > Resource > Working time
Then assign this calendar to a resource (related with an user) or a project

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

[1] 'Open tasks' means tasks in a stage that are defined with 'fold' = False

This a typical use case:

1. Create a project and configure:
    * Calculation type, for example "Date end"
    * Date end
2. Create tasks, configuring for each one:
    * From days, in this example, days from date end when this task must start
    * Estimation days, duration of the task in days
3. Click at "Recalculate project" button.
4. Go to task list in Gantt view and see the recalculated planning

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/8.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/vertical-service/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/vertical-service/issues/new?body=module:%20project_recalculate%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Endika Iglesias <endikaig@antiun.com>
* Rafael Blasco <rafabn@antiun.com>
* Antonio Espinosa <antonioea@antiun.com>
* Javier Iniesta <javieria@antiun.com>

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
