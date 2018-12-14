# -*- coding: utf-8 -*-

# © 2017 Le Filament (<http://www.le-filament.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class SaleProjectWizard(models.TransientModel):
    _name = 'sale.project.wizard'
    _description = 'Sale Project Assignment'

    @api.model
    def _default_sale_id(self):
        return self.env['sale.order'].browse(self.env.context.get('active_id'))

    @api.model
    def _default_project_project_id(self):
        return self._default_sale_id().project_project_id

    @api.model
    def _default_related_project_id(self):
        return self._default_sale_id().related_project_id

    @api.model
    def _default_project_name(self):
        if self._default_sale_id().partner_id.is_company:
            return self._default_sale_id().partner_id.name
        else:
            return self._default_sale_id().partner_id.parent_id.name

    sale_id = fields.Many2one(
        'sale.order', string='Sale', default=_default_sale_id
        )
    project_id = fields.Many2one(
        'project.project',
        string='Existing project',
        default=_default_project_project_id
        )
    project_name = fields.Char('New project', default=_default_project_name)
    related_project_id = fields.Many2one(
        'account.analytic.account',
        string='Analytical account related',
        default=_default_related_project_id
        )
    related_project_name = fields.Char(
        'New Analytical Account', default=_default_project_name
        )

    @api.onchange('project_id')
    def onchange_project_id(self):
        self.related_project_id = self.project_id.analytic_account_id

    @api.multi
    def close_dialog(self):
        sale_id = self.env['sale.order'].browse(
            self.env.context.get('active_id')
            )
        if self.project_id:
            sale_id.project_id = self.project_id.analytic_account_id
            sale_id.project_project_id = self.project_id
            project_id_new = self.project_id.id
        else:
            sale_id._create_analytic_account(prefix=None)
            project_id_new = sale_id.project_id.project_create({
                'name': self.project_name,
                'use_tasks': True
                })
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
        alias_prefix = self.env['ir.values'].get_default(
            'project.config.settings', 'alias_prefix'
            )
        ir_values = self.env['ir.values'].get_default(
            'project.config.settings', 'generate_project_alias'
            )
        for line in sale_id.order_line:
            if line.product_id.track_service == 'project':
                if line.product_id.project_id:
                    project_id = line.product_id.project_id.id
                    stage = line.product_id.project_task_type_id
                    if sale_id.partner_id.is_company:
                        if stage.name:
                            name_task = (
                                sale_id.partner_id.name
                                + " - "
                                + stage.name
                                )
                        else:
                            name_task = sale_id.partner_id.name
                    else:
                        if stage.name:
                            name_task = (
                                sale_id.partner_id.parent_id.name
                                + " - "
                                + stage.name
                                )
                        else:
                            name_task = sale_id.partner_id.parent_id.name
                else:
                    stage = stage_new
                    project_id = project_id_new
                    name_task = line.name.split('\n', 1)[0]
                project_date = self.env['project.project'].browse(project_id)
                project_date.daily_price = daily_price
                if not line.product_id.project_id:
                    if ir_values and alias_prefix:
                        alias_name = alias_prefix + project_date.name
                        project_date.alias_name = alias_name
                planned_hours = (
                    (line.price_subtotal / daily_price) * hours_per_day
                    )
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
                    'partner_id': (sale_id.partner_id.id
                                   or self.partner_dest_id.id),
                    'user_id': self.env.uid,
                    'description': description_line + '</p><br/>',
                    'project_id': project_id,
                    'company_id': sale_id.company_id.id,
                    'stage_id': stage.id or '',
                    'sale_line_id': line.id,
                    'price_subtotal': line.price_subtotal,
                    'currency_id': line.currency_id.id
                    })
        sale_id.tasks_ids = self.env['project.task'].search([
            ('sale_line_id', 'in', sale_id.order_line.ids)
            ])
        sale_id.tasks_count = len(sale_id.tasks_ids)
        return {'type': 'ir.actions.act_window_close'}
