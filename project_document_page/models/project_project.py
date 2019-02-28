# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    document_page_ids = fields.One2many(
        string='Wiki',
        comodel_name='document.page',
        inverse_name='project_id'
    )
    document_page_count = fields.Integer(
        compute='_compute_document_page_count',
    )

    @api.multi
    def _compute_document_page_count(self):
        for rec in self:
            rec.document_page_count = len(rec.document_page_ids)
