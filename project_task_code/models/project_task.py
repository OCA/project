# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.osv import expression


class ProjectTask(models.Model):
    _inherit = 'project.task'

    code = fields.Char(
        string='Task Number',
        required=True,
        default='/',
        readonly=True,
        copy=False,
    )

    _sql_constraints = [
        (
            'project_task_unique_code',
            'UNIQUE (code)',
            _('The code must be unique!')
        ),
    ]

    def _get_next_task_code(self):
        """
        Returns the next code to assign to a Task.
        values contains the create values, when called from create()
        """
        self and self.ensure_one()
        return self.env['ir.sequence'].next_by_code('project.task')

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        for task in tasks:
            if task.code == '/':
                task.code = task._get_next_task_code()
        return tasks

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        task = super().copy(default)
        if task.code == '/':
            task.code = task._get_next_task_code()
        return task

    def name_get(self):
        result = super().name_get()
        new_result = []

        for task in result:
            rec = self.browse(task[0])
            name = '[%s] %s' % (rec.code, task[1])
            new_result.append((rec.id, name))
        return new_result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                '|',
                ('code', '=ilike', '%' + name + '%'),
                ('name', operator, name)
            ]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        tasks = self.search(domain + args, limit=limit)
        return tasks.name_get()
