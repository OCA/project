# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import models
from openerp import SUPERUSER_ID


def create_code_equal_to_id(cr):
    """
    With this pre-init-hook we want to avoid error when creating the UNIQUE
    code constraint when the module is installed and before the post-init-hook
    is launched.
    """
    cr.execute('ALTER TABLE project_task '
               'ADD COLUMN code character varying;')
    cr.execute('UPDATE project_task '
               'SET code = id;')


def assign_old_sequences(cr, registry):
    """
    This post-init-hook will update all existing task assigning them the
    corresponding sequence code.
    """
    task_obj = registry['project.task']
    sequence_obj = registry['ir.sequence']
    task_ids = task_obj.search(cr, SUPERUSER_ID, [], order="id")
    for task_id in task_ids:
        cr.execute('UPDATE project_task '
                   'SET code = %s '
                   'WHERE id = %s;',
                   (sequence_obj.next_by_code(
                       cr, SUPERUSER_ID, 'project.task'), task_id, ))
