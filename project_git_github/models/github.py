# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from dateutil.parser import parse

from odoo import models, fields, http

TYPE = [('github', 'GitHub')]


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
    def parse_github_header(self, type, raw_payload):
        headers = http.request.httprequest.headers
        action_type = self._map_github_action_type(headers)

        data = {
            "event": headers.get("X-GitHub-Event"),
            "delivery": headers.get("X-GitHub-Delivery"),
            "action_type": action_type,
            "action": self._format_action_name(action_type),
        }

        signature = headers.get("X-Hub-Signature", False)
        if signature:
            data["signature"] = str(signature)

        return data

    def _map_github_action_type(self, headers):
        event = headers.get("X-GitHub-Event")
        return event in self._github_supported_event_types() and event or False

    def _format_action_name(self, action_type):
        return "git_%s" % (action_type,)

    def _github_supported_event_types(self):
        return ["push", "delete", "ping"]

    # -------------------------------------------
    # Payload
    # -------------------------------------------
    def parse_github_payload(self, context):
        method_name = self, "parse_github_%s" % context.action_type
        parse_event_method = getattr(method_name)
        return parse_event_method(context)

    # -------------------------------------------
    # Action Push
    # -------------------------------------------
    def parse_github_push(self, context):
        return {
            "repository": self.parse_github_repository(context),
            "branches": [self.parse_github_branch(context)],
            "sender": self.parse_github_sender(context)
        }

    # -------------------------------------------
    # Action Delete
    # -------------------------------------------
    def parse_github_delete(self, context):
        return {
            "branches": [self.parse_github_branch(context, False)]
        }

    # -------------------------------------------
    # Paring methods
    # -------------------------------------------
    def parse_github_branch(self, context, commits=True):
        payload = context.raw_payload
        name = payload["ref"] and payload["ref"].rsplit('/', 1)[-1] or "None"
        data = {
            "name": name,
            "url": payload["compare"],
            "type": context.type,
            "repository_id": context.repository.id
        }

        if commits:
            data["commits"] = self.parse_github_commits(context)

        return data

    def parse_github_commits(self, context):
        commits = []
        for commit in context.raw_payload["commits"]:
            commits.append(self.parse_github_commit(context, commit))
        return commits

    def parse_github_commit(self, context, commit):
        return {
            "name": commit["id"][:8],
            "message": commit["message"] and commit["message"].strip() or '',
            "url": commit["url"],
            "type": context.type,
            "date": fields.Datetime.to_string(parse(commit["timestamp"])),
            'author': self.parse_github_commit_author(context, commit),
        }

    def parse_github_commit_author(self, context, commit):
        sender = context.raw_payload["sender"]
        author = commit["author"]

        data = {
            "name": author["name"],
            "username": author["username"],
            "email": author["email"].lower(),
            "type": context.type,
            "avatar": "",
            "url": "",
            "uuid": "",
        }

        if sender["login"] == author["username"]:
            data["avatar"] = sender["avatar_url"]
            data["url"] = sender["html_url"]
            data["uuid"] = sender["id"]

        return data

    def parse_github_sender(self, context):
        sender = context.raw_payload["sender"]
        return {
            "username": sender["login"],
            "type": context.type,
            "avatar": sender['avatar_url'],
            "url": sender['html_url'],
            "uuid": sender['id'],
        }

    def parse_github_repository(self, context):
        repository = context.raw_payload["repository"]
        return {
            "name": repository["name"],
            "uuid": repository["id"],
            "url": repository["html_url"],
            "type": context.type,
            'owner': self.parse_github_repository_owner(context)
        }

    def parse_github_repository_owner(self, context):
        owner = context.raw_payload["repository"]["owner"]
        return {
            "name": owner["name"],
            "username": owner["login"],
            "email": owner["email"],
            "uuid": owner["id"],
            "avatar": owner["avatar_url"],
            "url": owner["html_url"],
            "type": context.type,
        }
