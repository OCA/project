# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import functools
import logging
import re

import gitlab  # pylint: disable=W7935
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
        token = request.env['ir.config_parameter'].sudo().get_param(
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
            _logger.warning(error)
            return error
        return func(event)

    def _get_record_type_and_id(self, title):
        """Searches in the title of the MR for the task or ticket ID with the
        correct format and returns the type of record and id if it can find it.

        :param title: Title of the MR
        :type: string
        :return: Dictionary with the type of record and ID obtained from the
        title or False if the title does not contain a correct format.
        :rtype: dictionary or boolean
        """
        exp = (r'^(.*[ \(\[\<])?'
               r'(?P<type>t(ask)?|i(ssue)?|ticket?)#?(?P<id>\d+)'
               r'([\)\]\>:=, \.,].*)?$')
        match = re.match(exp, title, re.IGNORECASE)
        if match:
            return match.groupdict()
        return False

    def _link_record(self, event, id_found):
        """Add link to Gitlab to access Odoo ticket or task.
        Create the git.request related to ticket or task.
        """
        model = 'project.task'
        rec_type = 'task'
        if id_found['type'] in ['ticket', 'i', 'issue']:
            model = 'helpdesk.ticket'
            rec_type = 'ticket'
        record = request.env[model].sudo().browse(int(id_found['id']))
        if not record:
            message = _('The %s #%s cannot be found in Odoo.') % (
                rec_type, id_found['id'])
            self._post_gitlab_message(event, message)
            return False
        project_id = event['project']['id']
        merge_request_id = event['object_attributes']['iid']
        git_request = request.env['git.request'].sudo().search([
            ('id_request', '=', merge_request_id),
            ('id_project', '=', project_id),
        ])
        git_request_vals = self._prepare_git_request(record, event)
        if git_request:
            git_request.sudo().write(git_request_vals)
            return False
        git_request.sudo().create(git_request_vals)
        url = record._notify_get_action_link('view')
        message = _('Linked to Odoo %s [#%s](%s)') % (rec_type, record.id, url)
        self._post_gitlab_message(event, message)
        return True

    def _prepare_git_request(self, record, event):
        vals = {
            'id_request': event['object_attributes']['iid'],
            'id_project': event['project']['id'],
            'name': event['object_attributes']['title'],
            'wip': event['object_attributes']['work_in_progress'],
            'state': event['object_attributes']['state'],
            'url': event['object_attributes']['url'],
            'branch': event['object_attributes']['source_branch'],
            'last_commit': event['object_attributes']['last_commit']['id'],
        }
        user = request.env['res.users'].sudo().search([
            ('gitlab_username', '=', event['user']['username'])])
        if user:
            vals['user_id'] = user.id
        if record._name == 'project.task':
            vals['task_id'] = record.id
        else:
            vals['ticket_id'] = record.id
        return vals

    def _process_merge_request(self, event):
        """Post messages in helpdesk.ticket or project.task based on the
        title of the Merge Request.
        The title must contain the type of registry and the ID preceded by a #
        sign.

        Ex. [IMP] webhook_gitlab: new module task #1234
        """
        title = event['object_attributes']['title']
        id_found = self._get_record_type_and_id(title)
        if not id_found:
            message = request.env['ir.qweb'].render(
                'webhook_gitlab.gitlab_id_not_in_title')
            self._post_gitlab_message(event, message)
            return False
        return self._link_record(event, id_found)

    def _process_pipeline(self, event):
        """Process pipeline status and update git.request in task or ticket.
        The title must contain the type of registry and the ID preceded by a #
        sign.

        Ex. [IMP] webhook_gitlab: new module task #1234
        """
        git_request = request.env['git.request'].sudo().search([
            ('branch', '=', event['object_attributes']['ref']),
            ('last_commit', '=', event['object_attributes']['sha']),
        ])
        if git_request:
            git_request.sudo().write({
                'ci_status': event['object_attributes']['status'],
            })
        return True

    def _connect_gitlab(self):
        """Connect to gitlab instance and return gitlab object"""
        url = request.env['ir.config_parameter'].sudo(
            ).get_param('webhook_gitlab.gitlab_url')
        token = request.env['ir.config_parameter'].sudo().get_param(
            'webhook_gitlab.gitlab_token')
        return gitlab.Gitlab(url, private_token=token)

    def _post_gitlab_message(self, event, message):
        """Post a message in the merge request of a project """
        project_id = event['project']['id']
        merge_request_id = event['object_attributes']['iid']
        response = self._connect_gitlab()
        project = response.projects.get(project_id)
        merge_request = project.mergerequests.get(merge_request_id)
        merge_request.discussions.create({'body': message})
        return True
