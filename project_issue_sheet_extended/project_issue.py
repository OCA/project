# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 - 2015 Camptocamp
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models


class project_issue(models.Model):
    _inherit = 'project.issue'

    confirmation_email_sent = fields.Boolean(string='Confirmation Mail Sent',
                                             default=True),

    @api.one
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
        through message_process.

        This set the confirmation_email_sent to False so an automatic email
        can be sent.

        """
        if custom_values is None:
            custom_values = {}
        else:
            custom_values = custom_values.copy()
        custom_values.setdefault('confirmation_email_sent', False)

        return super(project_issue, self).message_new(
            self.env.cr, self.env.uid, msg,
            custom_values=custom_values, context=self.env.context)

    @api.multi
    def name_get(self):
        """
        Add id in display name
        """
        project_issue_obj = self.env['project.issue']
        res = [(r['id'], '[REF #%s] %s' % (r['id'], r['name']))
               for r in project_issue_obj.search_read(
                   [('id', 'in', self.ids)], ['id', 'name'])]
        return res

    @api.multi
    def get_root_project(self, account):
        project_obj = self.env['project.project']
        project = project_obj.search([('analytic_account_id',
                                       '=',
                                       account.id)])
        # Check if we have a project linked to it
        if not project and account.parent_id:
            return self.get_root_project(account.parent_id)
        return project

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """
        Allow to search on an ID of issue
        """
        if not args:
            args = []
        ids = []
        if 'account_id' in self.env.context:
            account_analytic_obj = self.env['account.analytic.account']
            account_analytic = account_analytic_obj.browse(
                self.env.context['account_id'])
            project_root = self.get_root_project(account_analytic)
            if project_root:
                args += [['project_id','=',project_root.id]]
        if name:
            if name.isdigit():
                ids = self.search([('id', '=', name)] + args, limit=limit)
            else:
                ids = self.search([('name', operator, name)] + args,
                                  limit=limit)
        else:
            ids = self.search([] + args, limit=limit)
        return ids.name_get()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
