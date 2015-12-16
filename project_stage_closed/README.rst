.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=========================
Project Task Stage Closed
=========================

Odoo provides a 'closed' flag on project task stages, but this flag
is in the sale_service module, which in turns pulls a lot of dependencies
such as sale, accounting, and procurement. In many circumstances,
it is desirable to have such a flag to indicate a task is closed,
without needing so many dependencies.

This module provides the flag in a way that is compatible with sale_service
but depending only on the project module.

Installation
============

There are no specific installation instructions for this module.

Configuration
=============

There are no specific configuration instructions for this module.

Usage
=====

To use this module, you need to:

 * go to Project > Configuration > Stages > Task Stages where
   the Closed flag is available on the form view.

 
.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/8.0

Known issues / Roadmap
======================

When `Odoo PR 8186 <https://github.com/odoo/odoo/pull/8186>`_ 
is merged, this module becomes unnecessary.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/project/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/project/issues/new?body=module:%20project_stage_closed%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Stéphane Bidoul <stephane.bidoul@acsone.eu>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
