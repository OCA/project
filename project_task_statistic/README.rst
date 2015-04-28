.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
Project Task Statistics
=======================

Adds a new tab Statistics to the task form, similar to the Issue statistics.
It could be used for information alone, to use with Automated Actions, or to
for SLA control.

Project Stages are mapped to canonical states, and:

  * "Date Opened" is the first date a Task entered into a "In Progress" or "Pending" state.
  * "Date Closed" is the last date a Task entered into a "Done" or "Cancelled" state.

Installation
============

No specific actions needed.
It automatically installs the dependency ``base_stage_state``.

Configuration
=============

Project Stages should be configured, to map them to canonical "States".
It's the movement between these states that will trigger the "Date Opened"
and "Date Closed" statistics.

Go to Project Stages, configure the State each Stage corresponds to.

Usage
=====

In the Task form, check the new "Statistics" tab.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/8.0

Known issues / Roadmap
======================

Currently only the Starting and Closing dates are stored.
Should also compute the days and working hours to Open and to Close.

Credits
=======

Contributors
------------

* Daniel Reis


Maintainer
===========

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

mission is to support the collaborative development of Odoo features and
promote its widespread use.

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/project/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

OCA, or the Odoo Community Association, is a nonprofit organization whose
To contribute to this module, please visit https://odoo-community.org.
