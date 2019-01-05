# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    gitlab_link = fields.Boolean(
        help='Technical field used to map if the record have link to the '
             'Merge Request'
    )
