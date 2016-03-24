# -*- coding: utf-8 -*-
# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import _, api, fields, exceptions, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    issue_closed = fields.Boolean(
        related='issue_id.stage_id.closed', readonly=True,
    )

    @api.onchange('account_id')
    def onchange_account_id_project_issue_timesheet_time_control(self):
        if self.issue_id.analytic_account_id != self.account_id:
            self.issue_id = False
        domain = {'issue_id': []}
        if self.account_id:
            project = self.env['project.project'].sudo().search(
                [('analytic_account_id', '=', self.account_id.id)], limit=1,
            )
            domain = {'issue_id': [('project_id', '=', project.id),
                                   ('stage_id.closed', '=', False)]}
        return {'domain': domain}

    @api.onchange('issue_id')
    def onchange_issue_id_project_issue_timesheet_time_control(self):
        if not self.issue_id:  # pragma: no cover
            return
        if self.issue_id.analytic_account_id != self.account_id:
            self.account_id = self.issue_id.analytic_account_id.id

    @api.multi
    def button_open_issue(self):
        for line in self.filtered('issue_id.project_id'):
            stage = self.env['project.task.type'].search(
                [('project_ids', '=', line.issue_id.project_id.id),
                 ('closed', '=', False)], limit=1,
            )
            if stage:
                line.issue_id.write({'stage_id': stage.id})

    @api.multi
    def button_close_issue(self):
        for line in self.filtered('issue_id.project_id'):
            stage = self.env['project.task.type'].search(
                [('project_ids', '=', line.issue_id.project_id.id),
                 ('closed', '=', True)], limit=1,
            )
            if not stage:  # pragma: no cover
                raise exceptions.UserError(
                    _("There isn't any stage with closed check. Please "
                      "mark any.")
                )
            line.issue_id.write({'stage_id': stage.id})
