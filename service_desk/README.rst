.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Available service desks/teams are defined as Projects.

Incoming requests and tasks can then be related to customer Contracts and
service locations through additional two additional fields provided by the
module. This is optional, and is defined on a per project basis.

Features:

* Project has new field "Use Analytic Account?",
  with options "Yes" and "Required"
* Task has new fields "Analytic Account/Contract" and "Location",
  visible or required depending on the Project's setting
* Analytic Account has a new field "Contact", where you can set it's
  location/address (a Partner). It will be picked as the default locations
  when the Analytic Account is selected in a Task or Issue.

Credits
=======

Contributors
------------

* Authored  by Daniel Reis (https://github.com/dreispt)
* Icon courtesy of Everaldo Coelho (Crystal icon set)

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
