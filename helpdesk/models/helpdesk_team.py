# © 2014 Joël Grand-Guillaume (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api, _
    
class HelpdeskTeam(models.Model):
    _name = "helpdesk.team" 
    _description = "Helpdesk Team"

    name = fields.Char(required=True)
    description = fields.Text(string='Description')
    alias_id = fields.Many2one(
        comodel_name='mail.alias', string='Email Alias (Issues)',
        ondelete="restrict")
    member_ids = fields.Many2many(
        'res.users', 'helpdesk_team_user_rel', 'helpdesk_team_id', 'user_id',
        string='Members')
    stage_ids = fields.Many2many(
        'helpdesk.stage', 'helpdesk_team_stage_rel', 'helpdesk_team_id', 'stage_id',
        string='Members')
    ticket_ids = fields.Many2many(
        'helpdesk.ticket', 'helpdesk_team_ticket_rel', 'helpdesk_team_id', 'ticket_id',
        string='Members')
    
