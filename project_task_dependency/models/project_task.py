# Copyright 2016-2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    dependency_task_ids = fields.Many2many(
        string='Dependencies',
        comodel_name='project.task',
        relation='project_task_dependency_task_rel',
        column1='task_id', column2='dependency_task_id'
    )

    recursive_dependency_task_ids = fields.Many2many(
        string='Recursive Dependencies',
        comodel_name='project.task',
        compute='_compute_dependency'
    )

    depending_task_ids = fields.Many2many(
        string='Depending Tasks',
        comodel_name='project.task',
        help='Tasks that are dependent on this task.',
        compute='_compute_dependency'
    )

    recursive_depending_task_ids = fields.Many2many(
        string='Recursive Depending Tasks',
        comodel_name='project.task',
        help='Tasks that are dependent on this task (recursive).',
        compute='_compute_dependency'
    )

    @api.multi
    @api.depends('dependency_task_ids')
    def _compute_dependency(self):
        for task in self:
            task.recursive_dependency_task_ids = task.get_dependency_tasks(
                task, True
            )
            task.depending_task_ids = task.get_depending_tasks(task)
            task.recursive_depending_task_ids = task.get_depending_tasks(
                task, True
            )

    @api.model
    def get_dependency_tasks(self, task, recursive=False):
        dependency_tasks = task.dependency_task_ids
        if recursive:
            for t in dependency_tasks:
                dependency_tasks += self.get_dependency_tasks(t, recursive)
        return dependency_tasks

    @api.model
    def get_depending_tasks(self, task, recursive=False):
        if not isinstance(task.id, models.NewId):
            depending_tasks = self.search([(
                'dependency_task_ids', 'in', task.id)
            ])
            if recursive:
                for t in depending_tasks:
                    depending_tasks += self.get_depending_tasks(t, recursive)
            return depending_tasks

    @api.constrains('dependency_task_ids')
    def _check_dependency_recursion(self):
        if not self._check_m2m_recursion('dependency_task_ids'):
            raise ValidationError(
                _('You cannot create recursive dependencies between tasks.')
            )
