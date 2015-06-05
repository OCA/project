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

You can define workday begin/end at company level:

* Workday Begin: Hour when work starts, by default 08:00
* Workday End: Hour when work ends, by default 17:00


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


Credits
=======

Contributors
------------

* Endika Iglesias <endikaig@antiun.com>
* Rafael Blasco <rafabn@antiun.com>
* Antonio Espinosa <antonioea@antiun.com>


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
