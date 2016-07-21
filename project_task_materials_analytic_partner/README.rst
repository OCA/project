.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Partner in task materials
=========================

This module adds the partner on task materials and propagate it to the
auto-generated analytic entries on the "Other partner" field.

Installation
============

It requires the module *analytic_partner_hr_timesheet_invoice*, that it's
hosted on https://github.com/OCA/account-analytic.

Usage
=====

Go to Project > Tasks, and you will find the partner field in material lines.

Using this partner, when you invoice these materials, the target of the invoice
will be this partner instead the one in the project.

*Invoiceable* field is also added for selecting the invoicing ratio.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/87/8.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/
project/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/
project/issues/new?body=module:%20
project_task_analytic_partner%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------
* Carlos Dauden <carlos.dauden@tecnativa.com>
* Pedro M. Baeza <pedro.baeza@tecnativa.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
