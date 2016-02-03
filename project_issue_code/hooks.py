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

from openerp import SUPERUSER_ID


def create_code_equal_to_id(cr):
    """
    With this pre-init-hook we want to avoid error when creating the UNIQUE
    code constraint when the module is installed and before the post-init-hook
    is launched.
    """
    cr.execute('ALTER TABLE project_issue '
               'ADD COLUMN issue_code character varying;')
    cr.execute('UPDATE project_issue '
               'SET issue_code = id;')


def assign_old_sequences(cr, registry):
    """
    This post-init-hook will update all existing issue assigning them the
    corresponding sequence code.
    """
    issue_obj = registry['project.issue']
    sequence_obj = registry['ir.sequence']
    issue_ids = issue_obj.search(cr, SUPERUSER_ID, [], order="id")
    for issue_id in issue_ids:
        cr.execute('UPDATE project_issue '
                   'SET issue_code = \'%s\' '
                   'WHERE id = %d;' %
                   (sequence_obj.get(cr, SUPERUSER_ID, 'project.issue'),
                    issue_id))
