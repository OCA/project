# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import functools
import logging
import re

from odoo import http
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
        if task_str:
            task_id = int(re.sub(r'\D', '', title.split(task_str[0])[1]))
            task = request.env['project.task'].sudo().browse(task_id)
            task.message_post(subject="New Merge Request", body=body)
        if ticket_str:
            ticket_id = int(re.sub(r'\D', '', title.split(ticket_str[0])[1]))
            ticket = request.env['helpdesk.ticket'].sudo().browse(ticket_id)
            ticket.message_post(subject="New Merge Request", body=body)
        return True
