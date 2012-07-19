# -*- coding: utf-8 -*-
##############################################################################
#
#    Daniel Reis
#    2012
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
    'name': 'Email default template for Teams',
    'version': '6.1-1',
    "category": "Tools",
    'description': """\
New messages, created from the "Communication & History" tab, use a default template.
This default is defined by at (Sales/Service) Team level.
""",
    'author': 'Daniel Reis',
    'website': 'daniel.reis@securitas.pt',
    'depends': [
        'crm', #depends on Sales Teams
        'email_template', #extends the Compose Mail wizard
    ],
    'init_xml': [],
    'update_xml': [
        'crm_view.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
