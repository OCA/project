# -*- coding: utf-8 -*-
# © 2016 Michael Viriyananda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
