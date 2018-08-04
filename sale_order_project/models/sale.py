###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2014 Akretion (http://www.akretion.com).
#   Copyright (C) 2010-2013 Akretion LDTA (<http://www.akretion.com>)
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import api, models, _
from odoo.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_project_vals(self):
        self.ensure_one()
        name = " %s - %s - %s" % (
            self.partner_id.name,
            date.today().year,
            self.name)
        return {
            'user_id': self.user_id.id,
            'name': name,
            'partner_id': self.partner_id.id,
        }

    @api.multi
    def action_create_project(self):
        project_obj = self.env['project.project']
        for order in self:
            if order.project_id:
                raise Warning(_(
                    'There is a project already related with this sale order.'
                ))
            vals = order._prepare_project_vals()
            project = project_obj.create(vals)
            order.write({
                'project_id': project.analytic_account_id.id
            })
        return True
