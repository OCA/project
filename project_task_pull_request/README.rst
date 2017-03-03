.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Project Task Pull Request
=========================

This module extends the functionality of project to allow you to
add PR URIs to tasks and require PR URIs before tasks can be moved
to certain stages.

Usage
=====

To use this module, you need to:

#. Go to Project -> Configuration -> Project
#. Select a project and, under "Pull Request URIs", select the stages
   where you would like a PR URI to be required
#. Go to Dashboard and select a project
#. Attempt to move one of the project's task without a PR URI into one of
   the stages you selected to require a PR; you will receive a Validation Error
#. To add a PR URI to a task, click on the task and go to the "Extra Info" tag

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/10.0

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

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Kelly Lougheed <kelly@smdrugstore.com>

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
