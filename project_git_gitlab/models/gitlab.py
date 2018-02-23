# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

import re
from odoo import models, fields, http
from odoo.addons.project_git.utils.utils import urljoin

from dateutil.parser import parse

TYPE = [('gitlab', 'GitLab')]


class GitUser(models.Model):
    _inherit = 'project.git.user'

    type = fields.Selection(
        selection_add=TYPE,
    )


class GitRepository(models.Model):
    _inherit = 'project.git.repository'

    type = fields.Selection(
        selection_add=TYPE,
    )

    def _secret_visible_for_types(self):
        types = super(GitRepository, self)._secret_visible_for_types()
        types.append(TYPE[0][0])
        return types


class GitCommit(models.Model):
    _inherit = 'project.git.commit'

    type = fields.Selection(
        selection_add=TYPE,
    )


class GitBranch(models.Model):
    _inherit = 'project.git.branch'

    type = fields.Selection(
        selection_add=TYPE,
    )


class GitPayloadParser(models.AbstractModel):
    _inherit = 'project.git.payload.parser'

    # -------------------------------------------
    # Header
    # -------------------------------------------
    def parse_gitlab_header(self, type, raw_payload):
        headers = http.request.httprequest.headers
        action_type = self._map_gitlab_action_type(raw_payload)

        data = {
            "event": raw_payload['object_kind'],
            "delivery": raw_payload['checkout_sha'],
            "action_type": action_type,
            "action": self._format_action_name(action_type),
        }

        token = headers.get("X-Gitlab-Token", False)
        if token:
            data["token"] = token

        return data

    def _map_gitlab_action_type(self, raw_payload):

        def is_delete_event(evt):
            after = raw_payload['after']
            return evt == 'push' and (after.isdigit() and not int(after))

        event = raw_payload['object_kind']

        if event not in self._gitlab_supported_event_types():
            return False

        # In case of a push we need to check if we have a delete event
        if is_delete_event(event):
            event = 'delete'

        return event

    def _format_action_name(self, action_type):
        return "git_%s" % (action_type,)

    def _gitlab_supported_event_types(self):
        return ["push"]

    # -------------------------------------------
    # Payload
    # -------------------------------------------
    def parse_gitlab_payload(self, context):
        method_name = "parse_gitlab_%s" % context.action_type
        parse_event_method = getattr(self, method_name)
        return parse_event_method(context)

    # -------------------------------------------
    # Action Push
    # -------------------------------------------
    def parse_gitlab_push(self, context):
        return {
            "repository": self.parse_gitlab_repository(context),
            "branches": [self.parse_gitlab_branch(context)],
            "sender": self.parse_gitlab_sender(context)
        }

    # -------------------------------------------
    # Action Delete
    # -------------------------------------------
    def parse_gitlab_delete(self, context):
        return {
            "branches": [self.parse_gitlab_branch(context, False)]
        }

    # -------------------------------------------
    # Paring methods
    # -------------------------------------------
    def parse_gitlab_branch(self, context, commits=True):
        payload = context.raw_payload
        branch_name = payload["ref"].split('/')[-1]
        data = {
            "name": branch_name,
            "type": context.type,
            "repository_id": context.repository.id,
            "url": urljoin(
                payload['project']['homepage'] + '/', 'tree', branch_name
            ),
        }

        if commits:
            data["commits"] = self.parse_gitlab_commits(context)

        return data

    def parse_gitlab_commits(self, context):
        commits = []
        for commit in context.raw_payload["commits"]:
            commits.append(self.parse_gitlab_commit(context, commit))
        return commits

    def parse_gitlab_commit(self, context, commit):
        return {
            "name": commit["id"][:8],
            "message": commit["message"],
            "url": commit["url"],
            "date": fields.Datetime.to_string(parse(commit["timestamp"])),
            "type": context.type,
            "author": self.parse_gitlab_commit_author(context, commit),
        }

    def parse_gitlab_commit_author(self, context, commit):
        author_data = dict(
            name=commit["author"]["name"],
            email=commit["author"]["email"],
            type=context.type,
        )

        repository_owner = self.parse_gitlab_repository_owner(context)
        if repository_owner['email'] == author_data['email']:
            return repository_owner

        return author_data

    def parse_gitlab_sender(self, context):
        raw_payload = context.raw_payload

        return {
            "name": raw_payload["user_name"],
            "username": raw_payload["user_username"],
            "email": raw_payload["user_email"],
            "uuid": raw_payload["user_id"],
            "avatar": raw_payload["user_avatar"],
            "type": context.type,
        }

    def parse_gitlab_repository(self, context):
        project = context.raw_payload["project"]
        return {
            "name": project["name"],
            "full_name": project["path_with_namespace"],
            "url": project['homepage'],
            "type": context.type,
            "owner": self.parse_gitlab_repository_owner(context)
        }

    def parse_gitlab_repository_owner(self, context):
        raw_payload = context.raw_payload

        utils = re.search(
            r"(https?://.+/)(.+)/.+",
            raw_payload["repository"]["git_http_url"]
        )

        link = utils.group(1)
        username = utils.group(2)

        data = {
            "name": username.title(),
            "username": username,
            "uuid": "",
            "avatar": "",
            "url": urljoin(link, username),
            "email": "",
            "type": context.type,
        }

        if username == raw_payload["user_username"]:
            data["name"] = raw_payload["user_name"]
            data["uuid"] = raw_payload["user_id"]
            data["avatar"] = urljoin(link, raw_payload["user_avatar"])
            data["email"] = raw_payload["user_email"]

        return data
