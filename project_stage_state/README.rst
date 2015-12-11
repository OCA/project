.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Project States
==============

This module restores the ``state`` fields to Project Stages, removed in Odoo 8.0.

For some use cases it‘s necessary to be able to map the multiple Stages into 
a few broad groups.

For example, this can allow to define automated actions and business logic for 
Tasks not yet “Started”, knowing that “Started” means different Stages in 
different Projects.

Additionally adds a “Folded in Statusbar” flag to Stages, giving control on
the stages visible on Tasks and Issues Stage statusbar.

Configuration
=============

After instyalling thsi module you should consider reviewing your Project Stages
to configure wich ones should be directly available on the statubar widgets.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/project-service/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/project-service/issues/new?body=module:%20{module_name}%0Aversion:%20{version}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* `Daniel Reis <https://github.com/dreispt>`_

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
