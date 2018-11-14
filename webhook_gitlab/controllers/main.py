# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import _, http
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
        body = _(
            '''
            <ul>
                <li>URL: %s</li>
                <li>Title: %s</li>
                <li>Created by: %s</li>
                <li>Username: %s</li>
            </ul>
            ''') % (
            event['object_attributes']['url'],
            title,
            event['user']['name'],
            event['user']['username']
        )
        if task_str:
            task_id = int(re.sub(r'\D', '', title.split(task_str[0])[1]))
            task = request.env['project.task'].sudo().browse(task_id)
            task.message_post(subject="New Merge Request", body=body)
        if ticket_str:
            ticket_id = int(re.sub(r'\D', '', title.split(ticket_str[0])[1]))
            ticket = request.env['helpdesk.ticket'].sudo().browse(ticket_id)
            ticket.message_post(subject="New Merge Request", body=body)
        return True
