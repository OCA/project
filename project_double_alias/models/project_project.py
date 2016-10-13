# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.html).

from openerp import api, exceptions, fields, models, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    second_alias_name = fields.Char(
        string='Alias Name (Issues)',
        help="The name of the email alias, e.g. 'jobs' if you want to catch "
             "emails for <jobs@example.odoo.com>")
    second_alias_id = fields.Many2one(
        comodel_name='mail.alias', string='Email Alias (Issues)',
        ondelete="restrict")
    alias_domain2 = fields.Char(related="alias_domain", readonly=True)

    @api.multi
    def _create_alias_issue(self):
        self.ensure_one()
        alias_obj = self.env['mail.alias'].with_context(
            alias_model_name='project.issue',
            alias_parent_model_name=self._name)
        alias_defaults = {'project_id': self.id}
        # This is if you have installed project_issue_sheet module
        if self.env['project.issue']._fields.get('analytic_account_id'):
            alias_defaults['analytic_account_id'] = (
                self.analytic_account_id.id)  # pragma: no cover
        return alias_obj.create({
            'alias_name': self.second_alias_name,
            'alias_contact': self.alias_contact,
            'alias_parent_thread_id': self.id,
            'alias_defaults': alias_defaults,
        })

    @api.multi
    @api.constrains('second_alias_name')
    def check_second_alias_name(self):
        if self.env.context.get('no_check'):
            return
        model = self.env['ir.model'].search([('model', '=', 'project.issue')])
        for project in self.filtered('second_alias_name'):
            alias = self.env['mail.alias'].search(
                [('alias_name', '=', project.second_alias_name)])
            if (alias and
                    (alias.alias_parent_thread_id != project.id or
                     alias.alias_model_id != model.id)):
                raise exceptions.ValidationError(
                    _('The alias for issues is already taken.'))

    @api.model
    def create(self, vals):
        # Force the use of the first alias for creating tasks
        if not self.env.context.get('not_force_alias_model'):
            vals['alias_model'] = 'project.task'
        project = super(ProjectProject, self).create(vals)
        if vals.get('second_alias_name'):
            alias = project._create_alias_issue()
            project.second_alias_id = alias.id
        return project

    @api.multi
    def write(self, vals):
        # Force the use of the first alias for creating tasks
        if not self.env.context.get('not_force_alias_model'):
            vals['alias_model'] = 'project.task'
        res = super(ProjectProject, self).write(vals)
        if 'second_alias_name' in vals:
            # This has to be place after the call to super for having the
            # constraint correctly evaluated
            for project in self:
                model = self.env['ir.model'].search(
                    [('model', '=', 'project.issue')])
                alias = self.env['mail.alias'].search(
                    [('alias_parent_thread_id', '=', project.id),
                     ('alias_model_id', '=', model.id)])
                if not alias:
                    alias = project._create_alias_issue()
                    project.second_alias_id = alias.id
                else:
                    if not vals['second_alias_name']:
                        project.second_alias_id = False
                        alias.unlink()
                    else:
                        alias.alias_name = vals['second_alias_name']
        if vals.get('alias_contact'):
            self.mapped('second_alias_id').write(
                {'alias_contact': vals['alias_contact']})
        return res

    @api.multi
    def unlink(self):
        """Remove linked second aliases after removing the project to avoid
        restrict ondelete error.
        """
        aliases = self.mapped('second_alias_id')
        res = super(ProjectProject, self).unlink()
        aliases.unlink()
        return res
