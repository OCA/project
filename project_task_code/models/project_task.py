# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# Copyright 2020 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    code = fields.Char(
        string='Task Number', required=True, default="/", readonly=True)

    _sql_constraints = [
        ('project_task_unique_code', 'UNIQUE (code)',
         _('The code must be unique!')),
    ]

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            vals['code'] = self.env['ir.sequence'].next_by_code('project.task')
        return super(ProjectTask, self).create(vals)

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default['code'] = self.env['ir.sequence'].next_by_code('project.task')
        return super(ProjectTask, self).copy(default)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        tasks = []
        code = self._name_search_parse_code(name)
        if code:
            # We are searching for codes
            tasks = self.search(
                [('code', '=ilike', code + '%')] + args,
                limit=limit).name_get()
            if limit and len(tasks) == limit:
                return tasks
        additional_args = args + [('id', 'not in', [i[0] for i in tasks])]
        return tasks + super(ProjectTask, self).name_search(
            name=name,
            args=additional_args,
            operator=operator,
            limit=limit and limit - len(tasks) or limit)

    @api.model
    def _name_search_parse_code(self, name):
        """ Check if user input looks like code """
        # Remove any whitespace from name
        name = name.lstrip()
        # Get the data record
        sequence_id = self.env.ref('project_task_code.sequence_task')
        prefix = sequence_id.prefix or ''
        # if user is typing only digits, return right away
        if name.isdigit():
            return prefix + name
        # Check if input could be code
        if (
            name.startswith(prefix) and
            name[len(prefix): len(name)].isdigit(),
        ):
            return name
        return False
