# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Michael Viriyananda
#    Copyright 2016 OpenSynergy Indonesia
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
    "name": "Project Issue Code",
    "version": "8.0.1.0.0",
    'author': 'Michael Viriyananda,Odoo Community Association (OCA)',
    "category": "Project Management",
    'summary': 'Adding Field Code For Project Issue',
    'website': 'http://github.com/mikevhe18',
    "license": "AGPL-3",
    'description': """
        This module provides an additional feature
        that allows project issue has a code.
    """,
    "depends": [
        "project_issue",
    ],
    "data": [
        "data/project_issue_sequence.xml",
        "views/project_issue_view.xml",
    ],
    "installable": True,
    "pre_init_hook": "create_code_equal_to_id",
    "post_init_hook": "assign_old_sequences",
}
