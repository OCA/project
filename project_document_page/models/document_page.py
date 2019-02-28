# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class DocumentPage(models.Model):
    _inherit = 'document.page'

    project_id = fields.Many2one(
        string='Project',
        comodel_name='project.project',
    )
