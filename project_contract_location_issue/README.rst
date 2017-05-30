.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================================
Contract and Location on Project Issues
=======================================

Allows to link Project Issues to Contracts (Analytic Accounts)
and service Locations (Customer Contacts/Addresses).
This is configured per Project, and may be options or require fields.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/9.0


Configuration
=============

For each of the Projects you need these fields to be available,
edit the Project settings and set the "Use Analytic Account?" field
to "Optional" or Required".

The Analytic Account form features a "Service Location" field,
that can be used to set the default service location to used
for that Contract.


Usage
=====

If the corresponding Project is properly configured,
when creating an Issue we will have two new fields available:

* "Contract/Analytic" to select the Contract the Issue is related to.
* "Location" to select the contact or address where the Issue should be fixed.
  The available contacts are limited to the Analytic Account's Partner.


Known issues / Roadmap
======================


Credits
=======

Contributors
------------

* Daniel Reis <dreis.pt at hotmail.com>


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
