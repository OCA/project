.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================================
Project Management Security Groups
==================================

Project User permissions are reduced, so that they cannot edit Tasks 
(or Issues) not in the "New" and "Cancelled" states.
This makes it suitable for end users, that can create new requests
(and edit or cancel while they are still drafts) but can't
modify them once their resolutuion has been started by the project team.

Two additional groups are added, based on the project User group:

* "User: Can Edit Tasks/Issues": is for the project team, 
  and can edit Tasks (or Issues) in any state.
* "User: Manage Own Projects": has additional permissions to create Projects
  and related configurations.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/9.0

Configuration
=============

The existing Project Stages need to be mapped into proper States.
That's how we know what are "New" and "Cancelled" items.
Check the "Project Stage State" module `documentation <https://github.com/OCA/project/tree/9.0/project_stage_state>`
for for information.

After installing this module, review the Users with access to the Project app,
since at least some of them will need to have their access group changed to one of the new ones.

Usage
=====


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
