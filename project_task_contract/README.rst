.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

A "Project" can represent a service team. In this case we will want for Tasks
to relate to customer Contracts (Analytic Accounts).

This module adds a "Analytic Account" to project Tasks, to be able to relate 
it to a customer contract.

This field can be made invisible, available or even mandatory through a setting
on each project.

For field service use cases, the service location can also be necessary.
A field for this is also made available in project Tasks.
It's default value can be set on Contracts, and can be changed to any of the
customer's addresses.

Feature summary:

* Project has new field "Use Analytic Account?",
  with options "Yes" and "Required"
* Task has new fields "Analytic Account/Contract" and "Location",
  visible or required depending on the Project's setting
* Analytic Account has a new field "Contact", where you can set it's
  location/address (a Partner). It will be picked as the default locations
  when the Analytic Account is selected in a Task or Issue.

Usage
=============

Setup guide:

* On Projects, set the "Use Analytic Account?" definition to "Yes" or "Required"
* On Contracts/Analytic Accounts set the "Contact" if you want to have a default
  location/address (a Partner)

After this, the "Contract" and "Location" fields will be available (possibly 
required)a on the Tasks for those Projects.

Credits
=======

Contributors
------------

* Authored  by Daniel Reis (https://github.com/dreispt)

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
