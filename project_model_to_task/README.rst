
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3


Project Model to Task
=====================

This module allows end users to create a task from any configured models
and automatically link it to the initial object via a reference field.


Usage
=====

To use this module, you need to:

* go to a model or object in tree or form view (ie Partner ou Product).
* select a record (if your are in tree view).
* select 'Create a related task' in the 'More' button.
* the task and its 'Task Origin' field is set: complete and save the task form.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/10.0


Configuration
=============

You can modify the behavior by overriding ```default_get``` method of the task.



Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/project/issues>`_.
In case of trouble, please check there if your task has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Sébastien BEAU <sebastien.beau@akretion.com>
* David BEAL <david.beal@akretion.com>
* Serpent Consulting Services Pvt. Ltd. <jay.vora@serpentcs.com>

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
