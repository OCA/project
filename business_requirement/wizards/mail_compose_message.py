# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def default_get(self, cr, uid, fields, context=None):
        """ Handle composition mode. Some details about context keys:
            - comment: default mode, model and ID of a record the user comments
                - default_model or active_model
                - default_res_id or active_id
            - reply: active_id of a message the user replies to
                - default_parent_id or message_id or active_id: ID of the
                    mail.message we reply to
                - message.res_model or default_model
                - message.res_id or default_res_id
            - mass_mail: model and IDs of records the user mass-mails
                - active_ids: record IDs
                - default_model or active_model
        """
        if context is None:
            context = {}
        result = super(MailComposeMessage, self).default_get(
            cr, uid, fields, context=context)

        # v6.1 compatibility mode
        result['composition_mode'] = result.get(
            'composition_mode', context.get(
                'mail.compose.message.mode', 'comment'))
        result['model'] = result.get('model', context.get('active_model'))
        result['res_id'] = result.get('res_id', context.get('active_id'))
        result['parent_id'] = result.get(
            'parent_id', context.get('message_id'))

        if not result['model'] or not self.pool.get(result['model']) or not \
                hasattr(self.pool[result['model']], 'message_post'):
            result['no_auto_thread'] = True

        # default values according to composition mode -
        # NOTE: reply is deprecated, fall back on comment
        if result['composition_mode'] == 'reply':
            result['composition_mode'] = 'comment'
        vals = {}
        if 'active_domain' in context:
            # not context.get() because we want to keep global [] domains
            vals['use_active_domain'] = True
            vals['active_domain'] = '%s' % context.get('active_domain')
        if result['composition_mode'] == 'comment':
            vals.update(self.get_record_data(cr, uid, result, context=context))

        for field in vals:
            if field in fields:
                # ---------------------------- changes start here 2016/03/08
                if field == 'subject':
                    # only if default_model is business.requirement
                    if context.get('default_model') == 'business.requirement':
                        if context.get('default_res_id'):
                            br_object = self.pool.get(context.get('default_model'))\
                                .browse(cr, uid, context['default_res_id'])
                            subject = 'Re: %s-%s' % (
                                br_object.name, br_object.description)
                            result[field] = subject
                else:
                    # ----------------------- changes ends here 2016/03/08
                    result[field] = vals[field]

        # TDE HACK: as mailboxes used default_model='res.users'
        # and default_res_id=uid (because of lack of an accessible pid),
        # creating a message on its own
        # profile may crash (res_users does not allow writing on it)
        # Posting on its own profile works (res_users redirect to res_partner)
        # but when creating the mail.message to create the mail.compose.message
        # access rights issues may rise
        # We therefore directly change the model and res_id
        if result['model'] == 'res.users' and result['res_id'] == uid:
            result['model'] = 'res.partner'
            result['res_id'] = self.pool.get(
                'res.users').browse(cr, uid, uid).partner_id.id

        if fields is not None:
            [result.pop(field, None)
                for field in result.keys() if field not in fields]
        return result
