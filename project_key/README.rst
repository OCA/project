.. image:: https://www.gnu.org/graphics/lgplv3-147x51.png
   :target: https://www.gnu.org/licenses/lgpl-3.0.en.html
   :alt: License: LGPL-v3

============
Project key
============

This module provides functionality to uniquely identify projects and tasks by simple ``key`` field.


Usage
=====

To use this module functionality you just need to:

On ``project.project`` level:

In Kanban View:

#. Go to Project > Dashboard
#. Create
#. Enter project name and use auto generated key or simply override value by entering your own key value.

In Tree View:

#. Go to Project > Configuration > Projects
#. Create
#. Enter project name and use auto generated key or simply override value by entering your own key value.

In form View:

#. Go to Project > Dashboard
#. Open the projects settings
#. Modify the "key" value
#. After modifying project key the key of any existing tasks related to that project will be updated automatically.

When you create a project, under the hood a ir.sequence record gets creted with prefix: ``<project-key>-``.

On ``project.task`` level:

#. Actually there is nothing to be done here
#. Task keys are auto generated based on project key value with per project auto incremented number (i.e. PA-1, PA-2, etc)

In browser address bar:

#. Navigate to your project by entering following url: http://<<your-domain>>/projects/PROJECT-KEY
#. Navigate to your task by entering following url: http://<<your-domain>>/tasks/TASK-KEY

Credits
=======

Contributors
------------

* Petar Najman <petar.najman@modoolar.com>
* Sladjan Kantar <sladjan.kantar@modoolar.com>

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
