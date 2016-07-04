# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class TaskCategory(models.Model):
    _name = 'task.category'

    name = fields.Char('Name', required=True, translate=True, select=True)
    description = fields.Char('Description', translate=True)
    active = fields.Boolean('Active', default=True)

    _order = 'name'

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
         'Name already exists.'),
    ]


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_categ_id = fields.Many2one(
        'task.category',
        'Task Category',
    )
