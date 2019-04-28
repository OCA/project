# -*- coding: utf-8 -*-
# Copyright 2019 Thore Baden
# Copyright 2019 Benjamin Brich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Project(models.Model):
    _inherit = 'project.project'

    is_template = fields.Boolean(default=False, copy=False)
    template_id = fields.Many2one(
        comodel_name='project.project',
        string='Template',
    )

    @api.multi
    def toggle_template(self):
        for record in self:
            record.is_template = not record.is_template

    @api.model
    def create(self, vals):
        if 'template_id' in vals and vals['template_id']:
            # load the template
            template = self.env['project.project'].browse(vals['template_id'])
            new_template = template.copy()
            # set correct name after copy action
            new_template.name = vals['name']
            new_template.template_id = vals['template_id']
            return new_template
        return super(Project, self).create(vals)
