.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

============================
Project Task Materials Stock
============================
Project Tasks allow to record time spent, but some activities, such as
Field Service, often require you to keep a record of the materials spent.

This module extends project_task_material module to consume products spent in
a task and create analytic lines to manage costs and create invoices.

Configuration
=============

#. If you are a project manager, go to Project > Configuration > Stages and
   check option 'Consume Material' in Task Stage to generate a stock move when
   the task is in that stage.
#. Go to Project -> Configuration - > Settings and enable option
   "Manage time estimation on tasks"

Usage
=====

#. Go to a task, edit, and add materials to be consumed on tab "Materials".
#. Move task to an stage on consume material are activated and moves and
   analytic lines will be created.
#. You can define default locations to consume material in tasks and projects.
   Locations preference order to consume materials is: locations set in tasks
   first, locations defined in project second and finally standard locations.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/9.0


Known issues / Roadmap
======================

* Add support for budgeted/expected materials.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/project/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback.

Credits
=======

Contributors
------------

* Rafael Blasco <rafabn@antiun.com>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Carlos Dauden <carlos@incaser.es>
* Sergio Teruel <sergio@incaser.es>
* Vicent Cubells <vicent.cubells@tecnativa.com>

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
