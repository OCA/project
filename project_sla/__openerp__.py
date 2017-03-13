# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Daniel Reis
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Service Level Agreements',
    'summary': 'Define SLAs for your Contracts',
    'version': '8.0.1.0.0',
    "category": "Project Management",
    'description': """\
Contract SLAs
===============

SLAs are assigned to Contracts, on the Analytic Account form, SLA Definition
separator. This is also where new SLA Definitions are created.

One Contract can have several SLA Definitions attached, allowing for
"composite SLAs". For example, a contract could have a Response Time SLA (time
to start resolution) and a Resolution Time SLA (time to close request).


SLA Controlled Documents
========================

Only Project Issue documents are made SLA controllable.
However, a framework is made available to easilly build extensions to make
other documents models SLA controlled.

SLA controlled documents have attached information on the list of SLA rules
they should meet (more than one in the case for composite SLAs) and a summary
SLA status:

  * "watching" the service level (it has SLA requirements to meet)
  * under "warning" (limit dates are close, special attention is needed)
  * "failed" (one on the SLA limits has not been met)
  * "achieved" (all SLA limits have been met)

Transient states, such as "watching" and "warning", are regularly updated by
a hourly scheduled job, that reevaluates the warning and limit dates against
the current time and changes the state when find dates that have been exceeded.

To decide what SLA Definitions apply for a specific document, first a lookup
is made for a ``analytic_account_id`` field. If not found, then it will
look up for the ``project_id`` and it's corresponding ``analytic_account_id``.

Specifically, the Service Desk module introduces a Analytic Account field for
Project Issues. This makes it possible for a Service Team (a "Project") to
have a generic SLA, but at the same time allow for some Contracts to have
specific SLAs (such as the case for "premium" service conditions).


SLA Definitions and Rules
=========================

New SLA Definitions are created from the Analytic Account form, SLA Definition
field.

Each definition can have one or more Rules.
The particular rule to use is decided by conditions, so that you can set
different service levels based on request attributes, such as Priority or
Category.
Each rule condition is evaluated in "sequence" order, and the first onea to met
is the one to be used.
In the simplest case, a single rule with no condition is just what is needed.

Each rule sets a number of hours until the "limit date", and the number of
hours until a "warning date". The former will be used to decide if the SLA
was achieved, and the later can be used for automatic alarms or escalation
procedures.

Time will be counted from creation date, until the "Control Date" specified for
the SLA Definition.  That would usually be the "Close" (time until resolution)
or the "Open" (time until response) dates.

The working calendar set in the related Project definitions will be used (see
the "Other Info" tab). If none is defined, a builtin "all days, 8-12 13-17"
default calendar is used.

A timezone and leave calendars will  also used, based on either the assigned
user (document's `user_id`) or on the current user.


Setup checklist
===============

The basic steps to configure SLAs for a Project are:

  * Set Project's Working Calendar, at Project definitions, "Other Info" tab
  * Go to the Project's Analytic Account form; create and set SLA Definitions
  * Use the "Reapply SLAs" button on the Analytic Account form
  * See Project Issue's calculated SLAs in the new "Service Levels" tab


Credits and Contributors
========================

  * Daniel Reis (https://launchpad.net/~dreis-pt)
  * David Vignoni, author of the icon from the KDE 3.x Nuvola icon theme
""",
    'author': "Daniel Reis,Odoo Community Association (OCA)",
    'website': 'https://odoo-community.org/',
    'license': 'AGPL-3',
    'depends': [
        'project_issue',
    ],
    'data': [
        'project_sla_view.xml',
        'project_sla_control_view.xml',
        'project_sla_control_data.xml',
        'analytic_account_view.xml',
        'project_view.xml',
        'project_issue_view.xml',
        'project_task_view.xml',
        'security/ir.model.access.csv',
        'report/report_sla_view.xml',
    ],
    'demo': ['project_sla_demo.xml'],
    'test': ['test/project_sla.yml'],
    'installable': True,
}
