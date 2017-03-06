.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

==============================
Project Timesheet Time Control
==============================

* This module adds a button at account analytic line level to compute the spent
  time, in minutes, from start date to the current moment.
* It adds a datetime field that replaces ``date`` field in tree view, and write
  date field with datetime field value.
* It also adds a filter by user and some groups by task and by user.
* Finally, it allows to open and close tasks from account analytic lines.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/9.0

Known issues / Roadmap
======================

* *sale_service* module adds a check at project stage called "Is a closed
  stage", but we can't use this check, because it has a lot of dependencies
  (including sale module), so we use the check "Folded in Tasks Pipeline" for
  considering if a task is closed or not.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/project/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/
project/issues/new?body=module:%20
project_timesheet_time_control%0Aversion:%20
9.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Antonio Espinosa <antonioea@antiun.com>
* Carlos Dauden <carlos@incaser.es>
* Sergio Teruel <sergio@incaser.es>

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
