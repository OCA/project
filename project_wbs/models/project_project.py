# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

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
    def name_get(self):
        res = []
        for project_item in self:
            data = []
            proj = project_item

            while proj:
                if proj and proj.name:
                    data.insert(0, proj.name)
                else:
                    data.insert(0, '')  # pragma: no cover
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
                    data.insert(0, '')  # pragma: no cover

                proj = proj.parent_id

            data = '/'.join(data)
            res.append((project_item.id, data))
        return res

    @api.multi
    @api.depends('parent_id')
    def _compute_child(self):
        for project_item in self:
            child_ids = self.search(
                [('parent_id', '=', project_item.analytic_account_id.id)]
            )
            project_item.project_child_complete_ids = child_ids

    @api.multi
    def _resolve_analytic_account_id_from_context(self):
        """
        Returns ID of parent analytic account based on the value of
        'default_parent_id'
        context key, or None if it cannot be resolved to a single
        account.analytic.account
        """
        context = self.env.context or {}
        if type(context.get('default_parent_id')) == int:
            return context['default_parent_id']
        return None

    def prepare_analytics_vals(self, vals):
        return {
            'name': vals.get('name', _('Unknown Analytic Account')),
            'company_id': vals.get('company_id', self.env.user.company_id.id),
            'partner_id': vals.get('partner_id'),
            'active': True,
        }

    project_child_complete_ids = fields.Many2many(
        comodel_name='project.project',
        string="Project Hierarchy",
        compute="_compute_child"
    )
    c_wbs_code = fields.Char(
        related="analytic_account_id.complete_wbs_code",
        string='WBS Code',
        readonly=True,
        store=True
    )
    account_class = fields.Selection(
        related='analytic_account_id.account_class',
        store=True,
        default='project',
    )

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default['code'] = self.env['ir.sequence'].next_by_code(
            'account.analytic.account.code')
        return super(Project, self).copy(default)

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
            res['context'] = ({
                'default_parent_id': (project.analytic_account_id and
                                      project.analytic_account_id.id or
                                      False),
                'default_partner_id': (project.partner_id and
                                       project.partner_id.id or
                                       False),
                'default_user_id': (project.user_id and
                                    project.user_id.id or
                                    False),
            })
        domain.append(('id', 'in', project_ids))
        res.update({
            "display_name": project.name,
            "domain": domain,
            "nodestroy": False
        })
        return res

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
            res.update({
                "domain": domain,
                "nodestroy": False
            })
        res['display_name'] = project.name
        return res

    @api.multi
    def write(self, vals):
        res = super(Project, self).write(vals)
        if 'parent_id' in vals:
            for account in self.env['account.analytic.account'].browse(
                    self.analytic_account_id.get_child_accounts().keys()):
                account._complete_wbs_code_calc()
                account._complete_wbs_name_calc()
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
    @api.onchange('parent_id')
    def on_change_parent(self):
        self.analytic_account_id._onchange_parent_id()

    @api.multi
    def action_open_view_project_form(self):
        self.with_context(view_buttons=True)
        view = {
            'name': _('Details'),
            'view_type': 'form',
            'view_mode': 'form,tree,kanban',
            'res_model': 'project.project',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id,
            'context': self.env.context
        }
        return view
