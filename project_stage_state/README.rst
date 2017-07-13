.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================
Add State field to Project Stages
=================================

This module restores the `state` fields to Project Stages, removed in Odoo 8.0.

For some use cases it‘s necessary to be able to map the multiple Stages into
a few broad groups.

For example, this can allow to define automated actions and business logic for
Tasks not yet “Started”, knowing that “Started” means different Stages in
different Projects.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/9.0


Configuration
=============

For each Project Stage the corresponding canonical "State" should be chosen.
This can be done at iProject / Configuration / Stages.


Usage
=====

The "State" of each Task can be seen in the "Extra Info" tab.


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
