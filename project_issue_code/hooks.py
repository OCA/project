# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID
from odoo.api import Environment


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


def assign_old_sequences(cr, pool):
    """
    This post-init-hook will update all existing issue assigning them the
    corresponding sequence code.
    """
    env = Environment(cr, SUPERUSER_ID, {})
    issue_obj = env['project.issue']
    sequence_obj = env['ir.sequence']
    issue_ids = issue_obj.search([], order="id")
    for issue_id in issue_ids:
        issue_code = sequence_obj.next_by_code('project.issue')
        cr.execute('UPDATE project_issue '
                   'SET issue_code = \'%s\' '
                   'WHERE id = %d;' %
                   (issue_code, issue_id))
