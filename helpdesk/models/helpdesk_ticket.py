# © 2014 Joël Grand-Guillaume (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api, _

class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Support Ticket'
    _date_name = "date_start"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    _order = "priority desc, name, id desc"

    active = fields.Boolean(default=True)
    name = fields.Char(string='Ticket Number', required=True, index=True)
    summary = fields.Char(string='Summary', track_visibility='always',
        required=True)
    description = fields.Html(string='Description')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ], default='0', index=True, string="Priority")
    stage_id = fields.Many2one('helpdesk.stage', string='Stage',
        track_visibility='onchange', index=True,
        copy=False)
    tag_ids = fields.Many2many('ticket.tags', string='Tags')
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True,
        help="A task's kanban state indicates special situations affecting it:\n"
             " * Grey is the default situation\n"
             " * Red indicates something is preventing the progress of this task\n"
             " * Green indicates the task is ready to be pulled to the next stage")
    date_start = fields.Datetime(string='Starting Date',
        default=fields.Datetime.now,
        index=True, copy=False)
    date_end = fields.Datetime(string='Ending Date',
        index=True, copy=False)
    date_assign = fields.Datetime(string='Assigning Date', index=True,
        copy=False, readonly=True)
    date_deadline = fields.Date(string='Deadline', index=True, copy=False)
    date_last_stage_update = fields.Datetime(string='Last Stage Update',
        default=fields.Datetime.now,
        index=True,
        copy=False,
        readonly=True)
    notes = fields.Text(string='Notes')
    user_id = fields.Many2one('res.users',
        string='Assigned to',
        default=lambda self: self.env.uid,
        index=True, track_visibility='always')
    partner_id = fields.Many2one('res.partner',
        string='Customer')
    company_id = fields.Many2one('res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    color = fields.Integer(string='Color Index')
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True, related_sudo=False)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True, related_sudo=False)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True, related_sudo=False)
    displayed_image_id = fields.Many2one('ir.attachment', domain="[('res_model', '=', 'helpdesk.task'), ('res_id', '=', id), ('mimetype', 'ilike', 'image')]", string='Cover Image')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('helpdesk.ticket')
        res = super(HelpdeskTicket, self).create(vals)
        return res
    
    
