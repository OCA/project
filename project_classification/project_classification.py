# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joël Grand-guillaume (Camptocamp)
#    Copyright 2011 Camptocamp SA
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
from openerp import api, models, fields


class ProjectClassification(models.Model):
    _name = "project.classification"
    _description = "Project classification"

    name = fields.Char('Classification Name', required=True)
    project_id = fields.Many2one('account.analytic.account',
                                 'Parent project',
                                 help="The parent project that will be set "
                                 "when choosing this classification in "
                                 "a project.",
                                 required=True)
    to_invoice = fields.Many2one('hr_timesheet_invoice.factor',
                                 'Reinvoice Costs',
                                 help="Fill this field if you plan to "
                                 "automatically generate invoices based "
                                 "on the costs in this classification")
    currency_id = fields.Many2one('res.currency', 'Currency')
    user_id = fields.Many2one('res.users', 'Account Manager')
    pricelist_id = fields.Many2one('product.pricelist',
                                   'Sale Pricelist',
                                   domain=[('type', '=', 'sale')])


class ProjectProject(models.Model):
    _inherit = "project.project"

    classification_id = fields.Many2one('project.classification',
                                        'Classification',
                                        help="This will automatically set "
                                        "the parent project as well as other "
                                        "default values defined for this kind "
                                        "of project (like pricelist, "
                                        "invoice factor,..)",
                                        required=False,)

    child_project_complete_ids = fields.Many2many(
        'project.project',
        compute='_child_project_compute',
        string="Project Hierarchy")

    @api.one
    @api.depends('child_complete_ids.project_ids')
    def _child_project_compute(self):
        child_projects = self.mapped('child_complete_ids.project_ids')
        self.child_project_complete_ids = child_projects.sorted()

    @api.multi
    def onchange_classification_id(self, classification_id):
        projclass = self.env['project.classification']
        classification = projclass.browse(classification_id)
        return {'value':
                {'parent_id': classification.project_id.id,
                 'to_invoice': classification.to_invoice.id or False,
                 'currency_id': classification.currency_id.id or False,
                 'user_id': classification.user_id.id or False,
                 'pricelist_id': classification.pricelist_id.id or False}}
