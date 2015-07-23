.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Project classification (easy hierarchy and setup for project managers)
======================================================================


This Module allow you to setup different project classification to ease the
data entry of new project. The parent project will be set as readonly to
forbid users to change it.

The parent is still available through the analytic account object.
This is useful because this way, project manager will setup correctly
the analytical account just by choosing the corresponing classification.

A project classification is composed by :

 * A name
 * An Analytic Account which represent the parent project to set
 * An optional Invoice factor
 * An optional Account Manager
 * An optional Pricelist
 * An optional Currency

Those values will be set on a project when selecting a classification.


For further information, please visit:

* https://www.odoo.com/forum/help-1


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/project-service/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/project-service/issues/new?body=module:%20project_classification%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Daniel Reis <dgreis@sapo.pt>
* Joël Grand-Guillaume <joel.grandguillaume@camptocamp.com>
* Charbel Jacquin <charbel.jacquin@camptocamp.com>

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
