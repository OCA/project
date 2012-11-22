# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Daniel Reis
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
    'name': 'CRM Team default template for new e-mails',
    'version': '1',
    "category": "Tools",
    'description': """\
When a a new message is created, from the "Communication & History" tab, a blank message is displayed.
This module allows the definition of an e-mail template to use as default, so you can include company stationery
and even personalize with data from commonly used fields.
Definitions are made at: CRM -> Configuration -> Sales -> Sales Teams.

Known issues:
- It will only work correctly for the model for which the e-mail template was created.
""",
    'author': 'Daniel Reis',
    'website': 'daniel.reis@securitas.pt',
    'depends': [
        'crm',              #depends on Sales Teams
        'email_template',   #extends the Compose Mail wizard
    ],
    'update_xml': [
        'crm_view.xml',
    ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
