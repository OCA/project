# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from . import models
from openerp import SUPERUSER_ID


def create_code_equal_to_id(cr):
    cr.execute('ALTER TABLE project_task '
               'ADD COLUMN code character varying;')
    cr.execute('UPDATE project_task '
               'SET code = id;')


def assign_old_sequences(cr, registry):
    task_obj = registry['project.task']
    sequence_obj = registry['ir.sequence']
    task_ids = task_obj.search(cr, SUPERUSER_ID, [], order="id")
    for task_id in task_ids:
        cr.execute('UPDATE project_task '
                   'SET code = \'%s\' '
                   'WHERE id = %d;' %
                   (sequence_obj.get(cr, SUPERUSER_ID, 'project.task'),
                    task_id))
