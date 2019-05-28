# Copyright 2018 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.model
    def _get_default_phase_id(self):
        """ Gives default stage_id """
        return self.env['project.phase'].search([], order='sequence', limit=1)

    phase_id = fields.Many2one(
        comodel_name='project.phase', string='Phase',
        track_visibility='onchange', default=_get_default_phase_id,
        copy=False)
