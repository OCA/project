.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

======================
Project Security Group
======================

Project Security Group extends the standard rules to access at project and 
task records.

Role types:
-----------

* Project Manager: with full access.
Suitable for a PMO or Projects Director
No record rule limitation: sees all projects and all tasks/issues.

* Project Responsible: can create Projects and maintain things like Tags and 
Stages.
Suitable for the Project Managers responsible for specific projects.

* Project User: these are the people assigned to work on projects. 
They should be able to freely edit Tasks and Issues, but not configurations.
Suitable for Project Team Members adding permissions to be able to create 
issues.

* Project End Users: can open new Tasks/Issues but can't "manage" them.
Suitable for collaborators outside the projects. 
Add restrictions to the editable stages/states (requires dependency on 
project_stage_state).

Configuration
=============

* Limit project users - Limit project user to see only the task and issue
he/she is assigned and not all the task of a project. If project user is a
team member then he/she has permission to see all tasks and issues of a project.
* Limit task to team members - Add option not activated by default that if
activated will limit the users that can be assigned to a Task to the team
members. By default all project users can be assigned to a task even if they
are not members of the project team.

Usage
=====
.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/8.0

Known issues / Roadmap
======================

* Add support for access control to specific projects and tasks.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/project/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/project/issues/new?body=module:%20project_security_group%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

License
=======

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/agpl-3.0-standalone.html>.


Credits
=======

Contributors
------------

* Daniel Reis
* Rafael Blasco <rafabn@antiun.com>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Carlos Dauden <carlos@incaser.es>
* Sergio Teruel <sergio@incaser.es>

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

