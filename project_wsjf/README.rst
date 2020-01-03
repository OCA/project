.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============
Project Wsjf
============

        This module implements the Weighted Shortest Job First prioritization model.

        Weighted Shortest Job First (WSJF) is a prioritization model used to sequence jobs (eg., Features, Capabilities, and Epics) to produce maximum economic benefit. WSJF is estimated as the Cost of Delay (CoD) divided by job size.

        Calculating the Cost of Delay

        Four primary elements contribute to the Cost of Delay:
         - User-business value – Do our users prefer this over that? What is the revenue impact on our business? Is there a potential penalty or other adverse consequences if we delay?
         - Time criticality – How does the user/business value decay over time? Is there a fixed deadline? Will they wait for us or move to another solution? Are there Milestones on the critical path impacted by this?
         - Risk reduction-opportunity enablement value – What else does this do for our business? Does it reduce the risk of this or a future delivery? Is there value in the information we will receive? Will this feature open up new business opportunities?
         - Internal pressure – It is the pressure given internally, given a trade agreement, a defaulting customer, need for cash increase (work harder on a project that gives you more revenue)

        Duration

        Next, we need to understand the job duration. That can be pretty difficult to determine, especially early on when we might not know who is going to do the work or the capacity allocation for the teams. Fortunately, we have a ready proxy: job size. In systems with fixed resources, job size is a good proxy for the duration. (If I’m the only one mowing my lawn, and the front yard is three times bigger than the backyard, it’s going to take three times longer.) Also, we know how to estimate item size in Story points already. Taking job size, we have a reasonably straightforward calculation for comparing jobs via WSJF: WSJF = Cost of Delay / Job size.

Installation
============

This module depends on :
* project

Configuration
=============

There is nothing to configure.

Usage
=====

To use this module, you need only to install it. After installation, the fields
Business value, Time criticality, Risk reduction, Internal pressure and Job size will
appear in the projects and tasks forms. Filling these fields, the field WSJF will be
calculated and the order of presentation of the records will be given by the highest
value of WSJF.

Known issues / Roadmap
======================

* N/A

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/project/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Authors
-------

* KMEE INFORMATICA LTDA

Contributors
------------

* Gabriel Cardoso de Faria <gabriel.cardoso@kmee.com.br>

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
