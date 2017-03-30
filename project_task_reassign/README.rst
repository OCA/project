.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================================
Project and Resposible Reassign wizard
======================================

The Responsible (``user_id``) field is made read only, and can instead be
changed through a wizard, accessible only to Project Users.

Regular users (Employee group) will be able to see who is handling the request,
but won't be able to change it.

Project Users can click on the "=> Reassign" link, in front of the current
responsible, to open a dialog where they can select the new responsible and/or
new Project/Service Team it should be assigned to.

Mass reassignments can also be made, through the context menu action on the
list view.


Installation
============

No specific actions needed.


Configuration
=============

No configuration needed.


Usage
=====

Go to a Project Task, and click on the "=> Reassign" link, in front of the current
responsible.

This opens a dialog where we can select the new responsible and/or the 
new Project/Service Team it should be assigned to.

You may also go to the Task List view, select multiple Tasks, and pick the reassign
option from the top right context menu.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/8.0

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Known issues / Roadmap
======================

See the bugtracker.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/project/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

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
