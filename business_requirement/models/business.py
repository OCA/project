# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import except_orm
from openerp import tools
from openerp import SUPERUSER_ID


class BusinessRequirement(models.Model):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "business.requirement"
    _description = "Business Requirement"
    _order = 'id desc'

    @api.model
    def _get_default_company(self):
        company_id = self.env.user._get_company()
        if not company_id:
            raise except_orm(
                _('Error!'),
                _('There is no default company for the current user!'))
        return self.env['res.company'].browse(company_id)

    sequence = fields.Char(
        'Sequence',
        readonly=True,
        copy=False,
        index=True,
    )
    name = fields.Char(
        'Name',
        required=False,
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]}
    )
    description = fields.Char(
        'Description', required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    business_requirement = fields.Text(
        'Customer Story',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    scenario = fields.Text(
        'Scenario',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    gap = fields.Text(
        'Gap',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    business_requirement_categ_id = fields.Many2many(
        'business.requirement.category',
        string='Business Requirement Categ',
        relation='business_requirement_category_rel',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    state = fields.Selection(
        selection="_get_states",
        string='State',
        default='draft',
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange'
    )
    business_requirement_ids = fields.One2many(
        comodel_name='business.requirement',
        inverse_name='parent_id',
        string='Sub Business Requirement',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    parent_id = fields.Many2one(
        comodel_name='business.requirement',
        string='Parent',
        ondelete='set null',
        domain="[('id', '!=', id)]",
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    level = fields.Integer(
        compute='_get_level',
        string='Level',
        store=True
    )
    change_request = fields.Boolean(
        string='Change Request?',
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Master Project',
        ondelete='set null',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        store=True,
    )
    sub_br_count = fields.Integer(
        string='Count',
        compute='_sub_br_count'
    )
    priority = fields.Selection(
        [('0', 'Low'), ('1', 'Normal'), ('2', 'High')],
        'Priority',
        required=True,
        default='1'
    )
    confirmation_date = fields.Datetime(
        string='Confirmation Date',
        readonly=True
    )
    confirmed_id = fields.Many2one(
        'res.users', string='Confirmed by',
        readonly=True
    )
    approval_date = fields.Datetime(
        string='Approval Date',
        readonly=True
    )
    approved_id = fields.Many2one(
        'res.users',
        string='Approved by',
        readonly=True
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=_get_default_company,
    )

    @api.multi
    @api.onchange('project_id')
    def project_id_change(self):
        if self.project_id and self.project_id.partner_id:
            self.partner_id = self.project_id.partner_id.id

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('business.requirement')
        return super(BusinessRequirement, self).create(vals)

    @api.multi
    @api.depends('parent_id')
    def _get_level(self):
        def _compute_level(br):
            return br.parent_id and br.parent_id.level + 1 or 1

        for br in self:
            level = _compute_level(br)
            br.level = level

    @api.multi
    @api.depends('business_requirement_ids')
    def _sub_br_count(self):
        self.sub_br_count = len(self.business_requirement_ids)

    @api.model
    def _get_states(self):
        states = [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('approved', 'Approved'),
            ('customer_approval', 'Customer Approval'),
            ('in_progress', 'In progress'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
            ('drop', 'Drop'),
        ]
        return states

    @api.multi
    def action_button_confirm(self):
        self.write({'state': 'confirmed'})
        self.confirmed_id = self.env.user
        self.confirmation_date = fields.Datetime.now()

    @api.multi
    def action_button_back_draft(self):
        self.write({'state': 'draft'})
        self.confirmed_id = self.approved_id = []
        self.confirmation_date = self.approval_date = ''

    @api.multi
    def action_button_approve(self):
        self.write({'state': 'approved'})
        self.approved_id = self.env.user
        self.approval_date = fields.Datetime.now()

    @api.multi
    def action_button_customer_approval(self):
        self.write({'state': 'customer_approval'})

    @api.multi
    def action_button_in_progress(self):
        self.write({'state': 'in_progress'})

    @api.multi
    def action_button_done(self):
        self.write({'state': 'done'})

    @api.multi
    def action_button_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_button_drop(self):
        self.write({'state': 'drop'})

    @api.cr_uid_ids_context
    def message_post(self, cr, uid, thread_id, body='', subject=None,
                     type='notification', subtype=None, parent_id=False,
                     attachments=None, context=None,
                     content_subtype='html', **kwargs):
        # ---------------------------- changes start here 2016/03/08
        """
        Overwrite method message_post from mail.thread to modify the default
        behavior of subject with mail messages.
        """
        # ---------------------------- changes start here 2016/03/08
        """ Post a new message in an existing thread, returning the new
            mail.message ID.

            :param int thread_id: thread ID to post into, or list with one ID;
                if False/0, mail.message model will also be set as False
            :param str body: body of the message, usually raw HTML that will
                be sanitized
            :param str type: see mail_message.type field
            :param str content_subtype:: if plaintext: convert body into html
            :param int parent_id: handle reply to a previous message by adding
                the parent partners to the message in case of private
                discussion
            :param tuple(str,str) attachments or list id: list of attachment
                tuples in the form ``(name,content)``, where content is NOT
                base64 encoded

            Extra keyword arguments will be used as default column values
            for the new mail.message record. Special cases:
                - attachment_ids: supposed not attached to any document;
                    attach them to the related document.
                    Should only be set by Chatter.
            :return int: ID of newly created mail.message
        """
        # ---------------------------- changes start here 2016/03/08
        if context.get('default_model') == 'business.requirement':
            if context.get('default_res_id'):
                br_object = self.pool.get(context.get('default_model')).browse(
                    cr, uid, context['default_res_id'])
                subject = 'Re: %s-%s' % (br_object.name, br_object.description)
        # ---------------------------- changes start here 2016/03/08
        if context is None:
            context = {}
        if attachments is None:
            attachments = {}
        mail_message = self.pool.get('mail.message')

        assert (not thread_id) or \
            isinstance(thread_id, (int, long)) or \
            (isinstance(thread_id, (list, tuple)) and len(thread_id) == 1), \
            "Invalid thread_id; should be 0, False, \
                an ID or a list with one ID"
        if isinstance(thread_id, (list, tuple)):
            thread_id = thread_id[0]

        # if we're processing a message directly coming from the gateway,
        # the destination model was
        # set in the context.
        model = False
        if thread_id:
            model = context.get('thread_model', False) \
                if self._name == 'mail.thread' else self._name
            if model and model != self._name and \
                    hasattr(self.pool[model], 'message_post'):
                del context['thread_model']
                return self.pool[model].message_post(
                    cr, uid, thread_id, body=body, subject=subject, type=type,
                    subtype=subtype, parent_id=parent_id,
                    attachments=attachments, context=context,
                    content_subtype=content_subtype, **kwargs)

        # 0: Find the message's author,
        # because we need it for private discussion
        author_id = kwargs.get('author_id')
        if author_id is None:  # keep False values
            author_id = self.pool.get('mail.message')._get_default_author(
                cr, uid, context=context)

        # 1: Handle content subtype: if plaintext, converto into HTML
        if content_subtype == 'plaintext':
            body = tools.plaintext2html(body)

        # 2: Private message: add recipients
        # (recipients and author of parent message) - current author
        #   + legacy-code management (! we manage only 4 and 6 commands)
        partner_ids = set()
        kwargs_partner_ids = kwargs.pop('partner_ids', [])
        for partner_id in kwargs_partner_ids:
            if isinstance(
                partner_id,
                (list, tuple)
            ) and partner_id[0] == 4 and len(partner_id) == 2:
                partner_ids.add(partner_id[1])
            if isinstance(partner_id, (list, tuple)) and \
                    partner_id[0] == 6 and len(partner_id) == 3:
                partner_ids |= set(partner_id[2])
            elif isinstance(partner_id, (int, long)):
                partner_ids.add(partner_id)
            else:
                pass  # we do not manage anything else
        if parent_id and not model:
            parent_message = mail_message.browse(
                cr, uid, parent_id, context=context)
            private_followers = \
                set([partner.id for partner in parent_message.partner_ids])
            if parent_message.author_id:
                private_followers.add(parent_message.author_id.id)
            private_followers -= set([author_id])
            partner_ids |= private_followers

        # 3. Attachments
        #   - HACK TDE FIXME: Chatter: attachments linked to the document
        # (not done JS-side), load the message
        attachment_ids = self._message_preprocess_attachments(
            cr, uid, attachments,
            kwargs.pop('attachment_ids', []), model, thread_id, context)

        # 4: mail.message.subtype
        subtype_id = False
        if subtype:
            if '.' not in subtype:
                subtype = 'mail.%s' % subtype
            subtype_id = self.pool.get('ir.model.data').xmlid_to_res_id(
                cr, uid, subtype)

        # automatically subscribe recipients if asked to
        if context.get('mail_post_autofollow') and thread_id and partner_ids:
            partner_to_subscribe = partner_ids
            if context.get('mail_post_autofollow_partner_ids'):
                partner_to_subscribe = filter(lambda item: item in context.get(
                    'mail_post_autofollow_partner_ids'), partner_ids)
            self.message_subscribe(
                cr, uid, [thread_id],
                list(partner_to_subscribe), context=context)

        # _mail_flat_thread: automatically
        # set free messages to the first posted message
        if self._mail_flat_thread and model and not parent_id and thread_id:
            message_ids = mail_message.search(
                cr, uid, ['&', ('res_id', '=', thread_id),
                          ('model', '=', model),
                          ('type', '=', 'email')],
                context=context, order="id ASC", limit=1)
            if not message_ids:
                message_ids = message_ids = mail_message.search(
                    cr, uid, ['&', ('res_id', '=', thread_id),
                              ('model', '=', model)],
                    context=context, order="id ASC", limit=1)
            parent_id = message_ids and message_ids[0] or False
        # we want to set a parent: force to set the parent_id
        # to the oldest ancestor, to avoid having more than 1 level of thread
        elif parent_id:
            message_ids = mail_message.search(
                cr, SUPERUSER_ID,
                [('id', '=', parent_id),
                 ('parent_id', '!=', False)], context=context)
            # avoid loops when finding ancestors
            processed_list = []
            if message_ids:
                message = mail_message.browse(
                    cr,
                    SUPERUSER_ID,
                    message_ids[0],
                    context=context
                )
                while (
                    message.parent_id and (
                        message.parent_id.id not in processed_list
                    )
                ):
                    processed_list.append(message.parent_id.id)
                    message = message.parent_id
                parent_id = message.id

        values = kwargs
        values.update({
            'author_id': author_id,
            'model': model,
            'res_id': model and thread_id or False,
            'body': body,
            'subject': subject or False,
            'type': type,
            'parent_id': parent_id,
            'attachment_ids': attachment_ids,
            'subtype_id': subtype_id,
            'partner_ids': [(4, pid) for pid in partner_ids],
        })

        # Avoid warnings about non-existing fields
        for x in ('from', 'to', 'cc'):
            values.pop(x, None)

        # Post the message
        msg_id = mail_message.create(cr, uid, values, context=context)

        # Post-process: subscribe author, update message_last_post
        if model and model != 'mail.thread' and thread_id and subtype_id:
            # done with SUPERUSER_ID, because on some models users can post
            # only with read access, not necessarily write access
            self.write(
                cr, SUPERUSER_ID, [thread_id],
                {'message_last_post': fields.datetime.now()}, context=context)
        message = mail_message.browse(cr, uid, msg_id, context=context)
        if message.author_id and model and thread_id and \
                type != 'notification' and not \
                        context.get('mail_create_nosubscribe'):
            self.message_subscribe(
                cr, uid, [thread_id], [message.author_id.id], context=context)
        return msg_id


class BusinessRequirementCategory(models.Model):
    _name = "business.requirement.category"
    _description = "Business Requirement Category"

    name = fields.Char(string='Name', required=True)
    parent_id = fields.Many2one(
        comodel_name='business.requirement.category',
        string='Parent Category',
        ondelete='restrict'
    )
