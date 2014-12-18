# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Buron. Copyright Yannick Buron
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm


class ProjectAssignedPartnerConfig(orm.Model):

    """
    Extend the configuration line with field specific to partner assignment
    """

    _name = 'project.assigned.partner.config'
    _inherit = 'base.config.inherit.line'

    _columns = {
        'stage_id': fields.many2one(
            'project.task.type', 'Stage', required=True
        ),
        'partner_id': fields.many2one('res.partner', 'Assigned Partner'),
    }
