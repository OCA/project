# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class BusinessRequirementDeliverableCateg(models.Model):
    _inherit = "business.requirement.resource"

    task_categ_id = fields.Many2one(
        'task.category',
        string="Task Category"
    )

    @api.onchange('resource_type')
    def resource_type_change(self):
        super(BusinessRequirementDeliverableCateg, self).resource_type_change()
        if self.resource_type == 'procurement':
            self.task_categ_id = False
