# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, fields


class ProjectProject(models.Model):
    _inherit = "project.project"

    repository_ids = fields.One2many(
        comodel_name="project.git.repository",
        string="Repositories",
        inverse_name="project_id"
    )
