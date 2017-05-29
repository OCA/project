.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3
    
==================
Project Issue Code
==================

This module extends the functionality of project_issue that allows project issue has a code.
Issue Code will be automatically filled in accordance with the sequence.

Installation
============

To install this module, you need to:

1.  Clone the repository https://github.com/OCA/project
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Apps*
5.  Search For *Project Issue Code*
6.  Install the module

Usage
=====

After installing this module, every project issue will have:
    * A new field called "issue_code"
    * Project issue sequence
    
Field "issue_code" is readonly and its value will be filled in accordance with the sequence.
For the first time installation, the sequence is automatically configured.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/10.0


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

* Michael Viriyananda <viriyananda.michael@gmail.com>
* Dave Burkholder <dave@thinkwelldesigns.com>

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
