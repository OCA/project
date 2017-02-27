# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_categ_id = fields.Many2one(
        'project.category',
        'Task Category',
        required=True
    )
