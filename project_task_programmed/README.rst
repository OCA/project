.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Task Reminder Programmer
========================

Create automatically tasks as a reminder for any document (model) based on a date field.
The module is meant to remind (for example) a deadline by creating a task instead of an event.

If you want to plan the date when a new task will be created, based on a date of your document,
you should specify how much days in advance the task should be created.
Any date field can be used, for example a field that specifies a nearing deadline.

Let's say you have a generic object with deadline (or expiring date, or whatever date you prefer): 2016/04/01;
it doesn't matter whether the object is an invoice, an order, a task, an issue, etc...
Then with this module you can schedule that a new task will be created automatically one month before (2016/03/01).



Installation
============

To install this module, you need to:

#. Just install the module.

Configuration
=============

By default, a cron job named "Create alert tasks" will be created while installing this module.
This cron job can be found in:

	**Settings > Technical > Automation > Scheduled Actions**

This job runs daily by default.


Usage
=====

To use this functionality, you need to:

#. Create a project to which the new tasks will be related.
#. Go to the Task Alerts Configuration (Project > Configuration Task Alerts) and create a new record.
#. Add a name, a description of the task, who the task will be assigned to, etc...

The cron job will do the rest.

If you want to create the tasks manually, click on the button "Create Alerts"
in the Task Alerts Configuration form. This functionality is only
available for group Technical Features.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/8.0


Known issues / Roadmap
======================



Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/project/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Andrea Stirpe <a.stirpe@onestein.nl>


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
