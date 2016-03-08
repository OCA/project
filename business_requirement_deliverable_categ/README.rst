.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================================
Business Requirement Deliverable Task Category
==============================================

This module extends module business_requirement_deliverable and business_requirement_projects.

In business requirement, when creating a new resource line for a "Task" resource, you can add the task category.

From the Business Requirement a project with task can be generated based on the resources lines. This module will add the task category from business requirement resource line into the corresponding generated task.

To get this functionality, in module business_requirement_deliverable, we integrate the field "task_categ_id" (from module project_task_categ).


Installation
============

To install this module, you need to:

 * have basic modules installed (project)

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/project/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
project/issues/new?body=module:%20
business_requirement_deliverable_categ%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Victor M. Martin <victor.martin@elico-corp.com>

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
