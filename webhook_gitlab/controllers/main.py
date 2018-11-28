# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import functools
import logging
import re

import gitlab
from odoo import _, http
from odoo.http import request
from odoo.tools import consteq

_logger = logging.getLogger(__name__)


def token_authorization(function):
    """Decorator for controllers with token authorization.
    it allows only requests with X-Gitlab-Token header present.

    Will returns an unsuccessful response whenever the token
    is invalid.
    """
    @functools.wraps(function)
    def wrapper(self, *args, **kw):
        headers = request.httprequest.headers
        gitlab_token = headers.get('X-Gitlab-Token')
        token = request.env['ir.config_parameter'].get_param(
            'webhook_gitlab.authorization_token')
        if gitlab_token is None or not consteq(gitlab_token, token):
            _logger.warning(
                "Token %s is not the expected", gitlab_token)
            return False
        return function(self, *args, **kw)
    return wrapper


class WebhookGitlab(http.Controller):

    @http.route(
        '/webhook_gitlab/webhook/', type='json', auth='public',
        csrf=False)
    @token_authorization
    def _process_webhook(self):
        """Receive the request from Gitlab and invoke functions based on
        'object_kind', then it calls the function with the name
        _process_<object_kind>
        """
        event = request.jsonrequest
        try:
            func = getattr(self, '_process_%s' % event['object_kind'])
        except AttributeError as error:
            _logger.warning(error.message)
            return error.message
        return func(event)

    def _process_merge_request(self, event):
        """Post messages in helpdesk.ticket or project.task based on the
        title of the Merge Request.
        The title must contain the type of registry and the ID preceded by a #
        sign.

        Ex. [IMP] webhook_gitlab: new module task #1234
        """
        title = event['object_attributes']['title']
        task_str = filter(
            lambda x: x in title,
            ['task #', 'tarea #', 't #', 'task#', 'tarea#', 't#'])
        ticket_str = filter(
            lambda x: x in title,
            ['ticket #', 'issue #', 'i #', 'ticket#', 'issue#', 'i#'])
        body = request.env['ir.qweb'].render(
            'webhook_gitlab.gitlab_new_merge_request', dict(event=event))
        project_id = event['project']['id']
        merge_request_id = event['object_attributes']['iid']
        base_url = request.env['ir.config_parameter'].get_param('web.base.url')
        if not ticket_str and not task_str:
            message = request.env['ir.qweb'].render(
                'webhook_gitlab.gitlab_id_not_in_title')
            self._post_gitlab_message(project_id, merge_request_id, message)
            return False
        if task_str:
            task_id = int(re.sub(r'\D', '', title.split(task_str[0])[1]))
            task = request.env['project.task'].sudo().search([
                ('id', '=', task_id), ('gitlab_link', '=', False)])
            if not task:
                return False
            task.gitlab_link = True
            task.message_post(body=body)
            url = base_url + task._notification_link_helper('view')
            message = _('Linked to Odoo task [#%s](%s)') % (task.id, url)
            self._post_gitlab_message(project_id, merge_request_id, message)
        if ticket_str:
            ticket_id = int(re.sub(r'\D', '', title.split(ticket_str[0])[1]))
            ticket = request.env['helpdesk.ticket'].sudo().search([
                ('id', '=', ticket_id), ('gitlab_link', '=', False)])
            if not ticket:
                return False
            ticket.gitlab_link = True
            ticket.message_post(body=body)
            url = base_url + ticket._notification_link_helper('view')
            message = _('Linked to Odoo ticket [#%s](%s)') % (ticket.id, url)
            self._post_gitlab_message(project_id, merge_request_id, message)
        return True

    def _connect_gitlab(self):
        """Connect to gitlab instance and return gitlab object"""
        url = request.env['ir.config_parameter'].get_param(
            'webhook_gitlab.gitlab_url')
        token = request.env['ir.config_parameter'].get_param(
            'webhook_gitlab.gitlab_token')
        return gitlab.Gitlab(url, private_token=token)

    def _post_gitlab_message(self, project_id, merge_request_id, message):
        """Post a message in the merge request of a project """
        gitlab = self._connect_gitlab()
        project = gitlab.projects.get(project_id)
        merge_request = project.mergerequests.get(merge_request_id)
        merge_request.discussions.create({'body': message})
        return True
