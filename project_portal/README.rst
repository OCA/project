.. image:: https://www.gnu.org/graphics/lgplv3-147x51.png
   :target: https://www.gnu.org/licenses/lgpl-3.0.en.html
   :alt: License: LGPL-v3

================
Project Portal
================

This module overrides methods of the project portal controller to make them more usable for other modules.

Usage
=====

To use this module functionality you just need to:


If you want to extend ``portal_my_projects`` method now you can do it by:

#. Overriding ``portal_my_projects_prepare_values`` in case you want to prepare your values for rendering.
#. Overriding ``portal_my_projects_render`` in case you want to replace renderer.

If you want to extend ``portal_my_project`` method now you can do it by:

#. Overriding ``portal_my_project_prepare_values`` in case you want to prepare your values for rendering.
#. Overriding ``portal_my_project_render`` in case you want to replace renderer.

If you want to extend ``portal_my_tasks`` method now you can do it by:

#. Overriding ``portal_my_tasks_prepare_searchbar`` in case you want to extend search bar.
#. Overriding ``portal_my_tasks_prepare_task_search`` in case you want to extend task search.
#. Overriding ``portal_my_tasks_prepare_task_search_domain`` in case you want to extend task search domain.
#. Overriding ``portal_my_tasks_prepare_values`` in case you want to prepare your values for rendering.
#. Overriding ``portal_my_tasks_render`` in case you want to replace renderer.

If you want to extend ``portal_my_task`` method now you can do it by:

#. Overriding ``portal_my_task_prepare_values`` in case you want to prepare your values for rendering.
#. Overriding ``portal_my_task_render`` in case you want to replace renderer.


Credits
=======


Contributors
------------

* Petar Najman <petar.najman@modoolar.com>


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
