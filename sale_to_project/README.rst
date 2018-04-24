.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Sale to Contract
================

This module adds a new wizard on the sales orders allowing to create a contract
with all or a selection of lines that will be used as recurring invoices.

Configuration
=============

To configure this module, you need to:

* No configuration is needed

Usage
=====

To use this module, you need to:

* Use the new button `Create Contract` on a sales order
* You can choose to create a contract from all the lines or a selection
  of lines

Known issues / Roadmap
======================

* when all lines are put in a contract, the sales order is set to done
  (for a sales order without delivery). When part of the lines are put
  in a contract and the rest in an invoice, the sales order is set to
  done too, even if the invoice is not paid. It might make think it is
  a bug, but the same behavior is observed when we generate an invoice
  from all the sales order lines using the "Invoice by line" wizard.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/project-service/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/project-service/issues/new?body=module: sale_to_project%0Aversion: 8.0%0A%0A**Steps to reproduce**%0A- ...%0A%0A**Current behavior**%0A%0A**Expected behavior**>`_.


Credits
=======

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
