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


class BrGenerateProjects(models.TransientModel):
    _inherit = 'br.generate.projects'

    @api.multi
    def _prepare_project_task(self, line, project_id):
        context = self.env.context
        default_uom = context and context.get('default_uom', False)
        product_uom_obj = self.env['product.uom']
        qty = product_uom_obj._compute_qty(
            line.uom_id.id, line.qty, default_uom)
        vals = {
            'name': line.task_name,
            'description': line.description,
            'sequence': line.sequence,
            'project_id': project_id,
            'planned_hours': qty,
            'br_resource_id': line.id,
            'user_id': line.user_id.id,
            'task_categ_id': line.task_categ_id.id,
        }
        return vals
