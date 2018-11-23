# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import http
from odoo.http import request


class WebhookGitlab(http.Controller):

    @http.route(
        '/webhook_gitlab/merge_request/', type='json', auth='public',
        csrf=False)
    def process_merge_request(self):
        event = request.jsonrequest
        if event['event_type'] != 'merge_request':
            return False
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
