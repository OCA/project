# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#             <contact@eficent.com>
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
    "name": "Analytic account code sequence",
    "version": "1.0",
    "author": "Eficent",
    "website": "www.eficent.com",
    "category": "Generic Modules/Projects & Services",
    "depends": ["base", "project", "analytic", "project_wbs"],
    "description": """
    """,
    "data": [
        "analytic_account_sequence_view.xml",
        "analytic_account_sequence_data.xml",
        "account_analytic_account_view.xml",
        "security/ir.model.access.csv",
    ],
    'test': [
    ],
    'installable': True,
    'active': False,
    'certificate': '',
    'application': True,
    'license': 'AGPL-3',
}
