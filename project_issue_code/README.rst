.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3
    
==================
Project Issue Code
==================

This module extends the functionality of project_issue that allows project issue has a code.
Issue Code will be automatically filled in accordance with the sequence.

Configuration
=============

After installing this module, every project issue will have:
    * A new field called "issue_code"
    * Project issue sequence
    
Field "issue_code" is readonly and its value will be filled in accordance with the sequence.
For the first time installation, the sequence is automatically configured.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/project/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
project/issues/new?body=module:%20
project_issue_code%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Michael Viriyananda <viriyananda.michael@gmail.com>

Inspired By:
- project_task_code <https://github.com/OCA/project/tree/8.0/project_task_code>
    * Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
    * Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
    * Ana Juaristi <anajuarist@avanzosc.es>

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
