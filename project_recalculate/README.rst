.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Project recalculate
===================

This module allows to recalculate tasks' start/end dates depending on project's
start/end dates.

There are two calcutation modes:

* **Date begin**: Task's start/end dates are recalculated from project's date begin
* **Date end**: Task's start/end dates are recalculated from project's date end

If the project start/end date is changed in the form view, then you have to
click "Recalculate proyect" button to recalculate all pending tasks
according to the new date.


Configuration
=============

You can define working calendar at Setting > Technical > Resource > Working time
Then assign this calendar to a resource (related with an user)

When calculating task dates, this addon will look at user assigned to the task:

* If user assigned:
    * Search first resource related with this user (normally user is related,
      only with one resource) and get its working calendar
    * If not found, search first working calendar of the company
    * If not found, then every day is workable an work starts at 08:00 and
      ends at 18:00
* If not user assigned:
    * Search first working calendar of the company
    * If not found, then every day is workable an work starts at 08:00 and
      ends at 18:00


Usage
=====

This a tipycal use case:

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
