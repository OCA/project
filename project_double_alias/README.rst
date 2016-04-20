.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Double alias in projects
========================

Odoo by default allows to define an alias to receive mails, but you can only
select to create tasks or claims related to the project, but not both.

This module makes possible to create an alias for each.

Installation
============

On installation time, this module will move all the existing project aliases
that point to issues to the second alias. If the configured alias is for tasks,
an alias for issues is searched in the system anyway for being linked.

This operation will be reverted back when uninstalling (move second aliases to
the first one when no alias is defined for tasks).

In case you have projects which have configured both aliases for tasks and
issues, both are preserved on uninstallation of this module, but you will
only have accessed to the task one.

Configuration
=============

#. Enable developer mode.
#. Go to *Settings > Parameters > System parameters*.
#. Create or edit the parameter with the name "mail.catchall.domain", and put
   as value the domain of your mail server.

Usage
=====

#. Go to a project
#. Access the "E-mails" tab.
#. Define a mail alias for the tasks and a mail alias for issues

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/9.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/project/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
project/issues/new?body=module:%20
project_double_alias%0Aversion:%20
9.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Original Odoo Project Icon
* `FontAwesome Icon <http://fontawesome.io>`_.

Contributors
------------

* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Carlos Dauden <carlos.dauden@tecnativa.com>

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
