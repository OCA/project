.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================================
Business Requirement Deliverable Task Category
==============================================

This module extends module business_requirement_deliverable and business_requirement_project.

In business requirement if create a new business requirement resource line and if it is for a "Task" resource you could add the task category.

Business requirement could generate a project that also will create task. This module will add the task category from business requirement resource line.

Business requirement resource line also has the task name. This module merge the task name with the Business Requirement name like "BR_name-Task_name".

Module business_requirement_deliverable:

* Add field task_categ_id


Module business_requirement_project:

* Prefill the task category with business.requirement.resource.line "task_categ_id" 
* Merge task name with business.requirement "name" and business.requirement.resource.line "task_name"

Installation
============

To install this module, you need to:

 * have basic modules installed (project)

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Elico-Corp/odoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/Elico-Corp/odoo/issues/new?body=module:%business_requirement_deliverable_categ%0Aversion:%20{8.0}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Victor M. Martin <victor.martin@elico-corp.com>

Maintainer
----------

.. image:: https://www.elico-corp.com/logo.png
:alt: Elico Corp
:target: https://www.elico-corp.com

This module is maintained by Elico Corporation.

Elico Corporation offers consulting services to implement open source management software in SMEs, with a strong involvement in quality of service.

Our headquarters are located in Shanghai with branches in Hong Kong, ShenZhen and Singapore servicing customers from Greater China, Asia Pacific, Europe, Americas, etc...