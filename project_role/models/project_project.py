# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    assignment_ids = fields.One2many(
        string='Project Assignments',
        comodel_name='project.assignment',
        inverse_name='project_id',
        track_visibility='onchange',
    )
    inherit_assignments = fields.Boolean(
        string='Inherit assignments',
        default=lambda self: self._default_inherit_assignments(),
    )
    limit_role_to_assignments = fields.Boolean(
        string='Limit role to assignments',
        default=lambda self: self._default_limit_role_to_assignments(),
    )

    @api.model
    def _default_inherit_assignments(self):
        company = self.env['res.company'].browse(
            self._context.get('company_id', self.env.user.company_id.id)
        )
        return company.project_inherit_assignments

    @api.model
    def _default_limit_role_to_assignments(self):
        company = self.env['res.company'].browse(
            self._context.get('company_id', self.env.user.company_id.id)
        )
        return company.project_limit_role_to_assignments

    @api.model
    def create(self, values):
        company = None
        if 'company_id' in values:
            company = self.env['res.company'].browse(values['company_id'])

        if company and 'inherit_assignments' not in values:
            values['inherit_assignments'] = (
                company.project_inherit_assignments
            )

        if company and 'limit_role_to_assignments' not in values:
            values['limit_role_to_assignments'] = (
                company.project_limit_role_to_assignments
            )

        return super().create(values)
