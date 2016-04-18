.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================================
Business Requirement Deliverable Cost Control
=============================================

Introduction
^^^^^^^^^^^^

This module is part of a set ("Business Requirement") and provides the basic 
models for business requirement management and project time/cost estimation.

|image7|

.. |image7| image:: static/img/bus_req_tree.png
   :width: 800 px
   :alt: Business Requirement List view 


The set comprises of multiple modules that can be used independently or not:

=========================================== ====================================
Module                                      Description
=========================================== ====================================
business_requirement                        Basic models and functions
business_requirement_project                Wizard to create project/tasks 
                                            from BR/resource lines
business_requirement_crm                    Wizard to create/update Sales 
                                            Quotation based on deliverables
business_requirement_deliverable            Adds deliverables and resources lines
business_requirement_deliverable_report     Adds printout to send BR and 
                                            deliverables to the customer
business_requirement_deliverable_default    Adds default resource lines for 
                                            deliverable products
business_requirement_deliverable_cost       Add sales and cost price for 
                                            estimation and profit control
business_requirement_deliverable_categ      Adds the possibility to have 
                                            tasks category in resources
=========================================== ====================================

Many other modules (business_requirement_*) completes this basic list.

What is a Business Requirement?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A Business requirement (BR) is the expression of a business need by a customer 
or internal project user. 
A BR can contain multiple different parts depending on the company needs:

* Customer Story: this is the requirement as expressed by the customer
* Scenario: How/where the current solution can provide a suitable scenario to 
  answer the customer story
* Gap: For the uncovered part of the scenario, elaborate the gap/need for specific 
  developments/setup
* Deliverables to be provided to the customer/user
* Resources necessary to achieve the deliverables
* Additional information (approval, cost control etc.)

These modules were originally designed for the service/IT industry but the 
requirement management is generic and can apply to many cases/industries (customer 
or internal projects):

* Construction
* Trading (New product development)
* Business Consultancy
* IT development

What is the difference between a BR and CRM lead?

* CRM leads are sales oriented
* BR are project and workload estimation oriented

How to use this module?
^^^^^^^^^^^^^^^^^^^^^^^

This module improves the cost control of the original module with the following:

* Estimation sales price on resource lines. It provides a simple way to 
  calculate the sales price of the deliverable based on the necessary 
  resources lines (see usage).
* Adds ACL for sales price and resource cost confidentiality.
* Creates a tab Cost control in the Business Requirement for simple Gross Profit
  control.
* Multi-currency compatible: sales price is valued at currency Pricelist and 
  converted back to the reporting company currency for the cost control.

Installation
============

No specific steps required

Configuration
=============

Users
^^^^^

* **Business Requirement Sales Estimates**: Can See the sales prices in DL and RL (ideal for sales/presales)
* **Business Requirement Cost Control**: Can See the cost prices for project profit control (Manager/Finance dept)

Without Sales Estimate nor Cost Control rights:

|image3|

.. |image3| image:: static/img/bus_req_acl1.png
   :width: 800 px
   :alt: No access to sales or cost control information (Simple user)

Without Cost Control rights:

|image4|

.. |image4| image:: static/img/bus_req_acl2.png
   :width: 800 px
   :alt: Access to sales price with no cost control (Salesmen)


With both Sales Estimate and Cost Control rights:

|image5|

.. |image5| image:: static/img/bus_req_acl3.png
   :width: 800 px
   :alt: Full access to sales price and cost control (Financial dept)


Estimation Pricelist
^^^^^^^^^^^^^^^^^^^^

You can define the Estimation price list in the Master Project which will be 
used in deliverable lines and sales price for the resource lines.


Usage
=====

#. In the BR, you can add as many deliverable lines as necessary. You can keep the price empty at that stage

#. Once the deliverable lines are created you can create as many resources lines as necessary in each DL. 

#. in RL, the estimation sales price will be display per resource

#. The total Revenue from the resource can be copied back to the deliverable line.

#. you can review the cost control tab of your BR as followed (only available for ACL Cost Control)

|image2|

.. |image2| image:: static/img/bus_req_control.png
   :width: 800 px
   :alt: Control your cost for the BR


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/140/8.0

Known issues / Roadmap
======================

* Display the currency in the cost control panel and deliverable

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/
project/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/
project/issues/new?body=module:%20
business_requirement_deliverable_cost%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

Eric Caudal<eric.caudal@elico-corp.com>
Alex Duan<alex.duan@elico-corp.com>
Xie XiaoPeng<xie.xiaopeng@elico-corp.com>
Luke Zheng<luke.zheng@elico-corp.com>

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
