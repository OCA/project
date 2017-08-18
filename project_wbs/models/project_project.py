# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import time
from datetime import datetime, date
from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = "project.project"
    _description = "WBS element"
    _order = "c_wbs_code"

    @api.multi
    def _get_project_analytic_wbs(self):
        result = {}
        self.env.cr.execute('''
            WITH RECURSIVE children AS (
            SELECT p.id as ppid, p.id as pid, a.id, a.parent_id
            FROM account_analytic_account a
            INNER JOIN project_project p
            ON a.id = p.analytic_account_id
            WHERE p.id IN %s
            UNION ALL
            SELECT b.ppid as ppid, p.id as pid, a.id, a.parent_id
            FROM account_analytic_account a
            INNER JOIN project_project p
            ON a.id = p.analytic_account_id
            JOIN children b ON(a.parent_id = b.id)
            --WHERE p.state not in ('template', 'cancelled')
            )
            SELECT * FROM children order by ppid
        ''', (tuple(self.ids),))
        res = self.env.cr.fetchall()
        for r in res:
            if r[0] in result:
                result[r[0]][r[1]] = r[2]
            else:
                result[r[0]] = {r[1]: r[2]}

        return result

    @api.multi
    def _get_project_wbs(self):
        result = []
        projects_data = self._get_project_analytic_wbs()
        for ppid in projects_data.values():
            result.extend(ppid.keys())
        return result

    @api.multi
    @api.depends('name')
    def name_get(self):
        res = []
        for project_item in self:
            data = []
            proj = project_item

            while proj:
                if proj and proj.name:
                    data.insert(0, proj.name)
                else:
                    data.insert(0, '')
                proj = proj.parent_id
            data = '/'.join(data)
            res2 = project_item.code_get()
            if res2 and res2[0][1]:
                data = '[' + res2[0][1] + '] ' + data

            res.append((project_item.id, data))
        return res

    @api.multi
    @api.depends('code')
    def code_get(self):
        res = []
        for project_item in self:
            data = []
            proj = project_item
            while proj:
                if proj.code:
                    data.insert(0, proj.code)
                else:
                    data.insert(0, '')

                proj = proj.parent_id

            data = '/'.join(data)
            res.append((project_item.id, data))
        return res

    @api.multi
    @api.depends('parent_id')
    def _child_compute(self):
        for project_item in self:
            child_ids = self.search(
                [('parent_id', '=', project_item.analytic_account_id.id)]
            )
            project_item.project_child_complete_ids = child_ids

    @api.multi
    def _get_analytic_complete_wbs_code(self):
        for project in self:
            project.c_wbs_code = \
                project.analytic_account_id.complete_wbs_code

    @api.multi
    def _complete_wbs_code_search_analytic(self):
        """ Finds projects for an analytic account.
        @return: List of ids
        """
        project_ids = self.search([('analytic_account_id', 'in', self.ids)])
        return project_ids

    project_child_complete_ids = fields.Many2many(
        'project.project',
        string="Project Hierarchy",
        compute=_child_compute
    )
    c_wbs_code = fields.Char(
        compute=_get_analytic_complete_wbs_code,
        string='WBS Code',
        readonly=True,
        store=True
    )
    account_class = fields.Selection(
        related='analytic_account_id.account_class',
        store=True,
    )
    # Override the standard behaviour of duplicate_template not introducing
    # the (copy) string to the copied projects.

    @api.multi
    def duplicate_template(self):
        data_obj = self.env['ir.model.data']
        result = []
        for proj in self:
            parent_id = self.env.context.get('parent_id', False)
            self = self.with_context(analytic_project_copy=True)
            new_date_start = time.strftime('%Y-%m-%d')
            new_date_end = False
            if proj.date_start and proj.date:
                start_date = date(
                    *time.strptime(proj.date_start, '%Y-%m-%d')[:3]
                )
                end_date = date(*time.strptime(proj.date, '%Y-%m-%d')[:3])
                new_date_end = (
                    datetime(
                        *time.strptime(
                            new_date_start,
                            '%Y-%m-%d'
                        )[:3]
                    ) + (end_date - start_date)
                ).strftime('%Y-%m-%d')
            self = self.with_context(copy=True)
            new_id = proj.copy(default={
                'name': _("%s") % proj.name,
                'state': 'open',
                'date_start': new_date_start,
                'date': new_date_end,
                'parent_id': parent_id})
            result.append(new_id)
            child_ids = self.search(
                [('parent_id', '=', proj.analytic_account_id.id)])
            parent_id = new_id.analytic_account_id.id
            if child_ids:
                self = self.with_context(parent_id=parent_id)
                self.duplicate_template(
                    child_ids, context={'parent_id': parent_id})
        if result and len(result):
            res_id = result[0]
            form_view_id = data_obj._get_id('project', 'edit_project')
            form_view = data_obj.read(form_view_id, ['res_id'])
            tree_view_id = data_obj._get_id('project', 'view_project')
            tree_view = data_obj.read(tree_view_id, ['res_id'])
            search_view_id = data_obj._get_id(
                'project', 'view_project_project_filter')
            search_view = data_obj.read(search_view_id, ['res_id'])
            return {
                'name': _('Projects'),
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'project.project',
                'view_id': False,
                'res_id': res_id,
                'views': [
                    (form_view['res_id'], 'form'),
                    (tree_view['res_id'], 'tree')
                ],
                'type': 'ir.actions.act_window',
                'search_view_id': search_view['res_id'],
                'nodestroy': True
            }

    @api.multi
    def action_open_child_view(self, module, act_window):
        """
        :return dict: dictionary value for created view
        """
        res = self.env['ir.actions.act_window'].for_xml_id(module, act_window)
        domain = []
        project_ids = []
        for project in self:
            child_project_ids = self.search(
                [('parent_id', '=', project.analytic_account_id.id)]
            )
            for child_project_id in child_project_ids:
                project_ids.append(child_project_id.id)
            if project_ids:
                def_parent_id = project.analytic_account_id and \
                    project.analytic_account_id.id or False
                def_partner_id = project.partner_id and \
                    project.partner_id.id or False
                default_user_id = \
                    project.user_id and project.user_id.id or False
                self = self.with_context(default_parent_id=def_parent_id,
                                         default_partner_id=def_partner_id,
                                         default_user_id=default_user_id)
                domain.append(('id', 'in', project_ids))
                res.update(domain=domain, nodestroy=False)
        return res

    @api.multi
    def action_open_projects_view(self):
        return self.action_open_child_view(
            'project_wbs', 'open_view_project_projects')

    @api.multi
    def action_open_child_tree_view(self):
        return self.action_open_child_view(
            'project_wbs', 'open_view_project_wbs')

    @api.multi
    def action_open_child_kanban_view(self):
        return self.action_open_child_view(
            'project_wbs', 'open_view_wbs_kanban')

    @api.multi
    def action_open_parent_tree_view(self):
        """
        :return dict: dictionary value for created view
        """
        domain = []
        analytic_account_ids = []
        res = self.env['ir.actions.act_window'].for_xml_id(
            'project_wbs', 'open_view_project_wbs'
        )
        for project in self:
            if project.parent_id:
                for parent_project_id in self.env['project.project'].search(
                        [('analytic_account_id', '=', project.parent_id.id)]
                ):
                    analytic_account_ids.append(parent_project_id.id)
        if analytic_account_ids:
            domain.append(('id', 'in', analytic_account_ids))
        return res

    @api.multi
    def action_open_parent_kanban_view(self):
        """
        :return dict: dictionary value for created view
        """
        domain = []
        analytic_account_ids = []
        res = self.env['ir.actions.act_window'].for_xml_id(
            'project_wbs', 'open_view_wbs_kanban'
        )
        for project in self:
            if project.parent_id:
                for parent_project_id in self.env['project.project'].search(
                        [('analytic_account_id', '=', project.parent_id.id)]
                ):
                    analytic_account_ids.append(parent_project_id.id)
        if analytic_account_ids:
            domain.append(('id', 'in', analytic_account_ids))
            res.update({
                "domain": domain,
                "nodestroy": False
            })
        return res

    @api.multi
    def button_save_data(self):
        return True

    @api.multi
    def action_open_view_project_form(self):
        self.with_context(view_buttons=True)
        view = {
            'name': _('Details'),
            'view_type': 'form',
            'view_mode': 'form,tree,kanban,gantt',
            'res_model': 'project.project',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id,
            'context': self.env.context
        }
        return view
