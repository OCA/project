# -*- coding: utf-8 -*-
# © 2017 Le Filament (<http://www.le-filament.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def saleorder_update_tasks(self):
        for order in self:
            stage_id_new = self.env['ir.values'].get_default(
                'sale.config.settings', 'project_task_type_id'
                )
            stage_new = self.env['project.task.type'].browse(stage_id_new)
            daily_price = self.env['ir.values'].get_default(
                'project.config.settings', 'daily_price'
                )
            hours_per_day = self.env['ir.values'].get_default(
                'project.config.settings', 'hours_per_day'
                )
            # loop over each order line
            for line in order.order_line:
                task_id_refer = self.env['project.task'].search(
                    [('sale_line_id', '=', line.id)]
                    )
                # if task already linked to this order line
                if task_id_refer:
                    # if price is to be updated
                    if line.price_subtotal != task_id_refer.price_subtotal:
                        # update planned_hours and price
                        planned_hours = (
                            (line.price_subtotal / daily_price) * hours_per_day
                            )
                        task_id_refer.planned_hours = planned_hours
                        task_id_refer.price_subtotal = line.price_subtotal
                else:
                    if line.product_id.track_service == 'project':
                        # if line product is assigned a default project
                        if line.product_id.project_id:
                            project_id = line.product_id.project_id.id
                            stage = line.product_id.project_task_type_id
                            if order.partner_id.is_company:
                                name_task = (
                                    order.partner_id.name + " - " + stage.name
                                    )
                            else:
                                name_task = (
                                     order.partner_id.parent_id.name
                                     + " - "
                                     + stage.name
                                     )
                        else:
                            stage = stage_new
                            project_id = order.project_project_id.id
                            name_task = line.name.split('\n', 1)[0]
                        planned_hours = (
                            (line.price_subtotal / daily_price) * hours_per_day
                            )
                        # set task description = order line description
                        description_line = "<p>"
                        for line_name in line.name:
                            if line_name == '\n':
                                description_line = description_line + "</p><p>"
                            else:
                                description_line = description_line + line_name
                        self.env['project.task'].create({
                            'name': name_task,
                            'planned_hours': planned_hours,
                            'remaining_hours': planned_hours,
                            'partner_id': (
                                           order.partner_id.id
                                           or self.partner_dest_id.id
                                           ),
                            'user_id': self.env.uid,
                            'description': description_line + '</p><br/>',
                            'project_id': project_id,
                            'company_id': order.company_id.id,
                            'stage_id': stage.id,
                            'sale_line_id': line.id
                            })
            order.tasks_ids = self.env['project.task'].search([
                ('sale_line_id', 'in', order.order_line.ids)
                ])
            order.tasks_count = len(order.tasks_ids)
