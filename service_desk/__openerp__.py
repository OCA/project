# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012-2013 Daniel Reis
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
    'name': 'Service Desk',
    'summary': 'Use Projects for Service Desks and service teams',
    'version': '1.1',
    "category": "Project Management",
    'description': """\
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

(Icon image credits to Everaldo Coelho, Crystal icon set)
""",
    'author': 'Daniel Reis',
    'website': '',
    'depends': [
        'project',
    ],
    'data': [
        'analytic_contact_view.xml',
        'service_desk_view.xml',
    ],
    'installable': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
