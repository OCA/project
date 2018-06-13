# © 2014 Joël Grand-Guillaume (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api, _
    
class TicketTags(models.Model):
    """ Tags of project's tasks """
    _name = "ticket.tags"
    _description = "Tags of tickets"

    name = fields.Char(required=True)
    color = fields.Integer(string='Color Index', default=10)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]
    
    
