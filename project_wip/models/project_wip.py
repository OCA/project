# Copyright 2019 KMEE INFORMÁTICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ProjectWip(models.Model):

    _name = 'project.wip'
    _description = 'Project Wip'  # TODO

    name = fields.Char()
