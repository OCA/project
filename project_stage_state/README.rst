.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
Project Stage State
===================

This module restores the `state` fields to Project Stages, removed in Odoo 8.0.

For some use cases it‘s necessary to be able to map the multiple Stages into
a few broad groups.

For example, this can allow to define automated actions and business logic for
Tasks not yet “Started”, knowing that “Started” means different Stages in
different Projects.

Usage
=====

To use this module, you need to:

#. Go to Project -> Configuration -> Stages and click on a stage
#. Select the state you would like to associate that stage with from the dropdown "State" menu
#. Save your changes
#. Go to Project -> Dashboard and click on a project
#. Click on task in the stage you just edited
#. Under the "Extra Info" tab, you can see the "State" field for that task

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: ttps://runbot.odoo-community.org/runbot/140/10.0

Known issues / Roadmap
======================

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/project/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Daniel Reis

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
