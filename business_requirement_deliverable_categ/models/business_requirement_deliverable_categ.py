# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class BusinessRequirementDeliverableCateg(models.Model):
    _inherit = "business.requirement.resource"

    task_categ_id = fields.Many2one(
        'task.category',
        string="Task Category"
    )
