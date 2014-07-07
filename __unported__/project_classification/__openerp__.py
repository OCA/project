# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joël Grand-guillaume (Camptocamp)
#    Copyright 2011 Camptocamp SA
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
    'name': 'Project classification (easy hierarchy and setup for project managers)',
    'version': '1.0',
    'category': 'Generic Modules/Projects & Services',
    'description': """

This Module allow you to setup different project classification to ease the data entry of
new project. The parent project will be set as readonly to forbid users to change it.
The parent is still available through the analytic account object. This is useful because
this way, project manager will setup correctly the analytical account just by choosing the
corresponing classification.

A project classification is composed by :

 * A name
 * An Analytic Account which represent the parent project to set
 * An optional Invoice factor
 * An optional Account Manager
 * An optional Pricelist
 * An optional Currency

Those values will be set on a project when selecting a classification.

""",
    'author': 'Camptocamp',
    'website': 'http://www.camptocamp.com',
    'depends': ['project', 'hr_timesheet_invoice', 'analytic'],
    'data': [
        'project_classification_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
