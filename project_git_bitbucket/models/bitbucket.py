# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

import re
from odoo import models, fields, http

TYPE = [("bitbucket", "BitBucket")]


class GitUser(models.Model):
    _inherit = "project.git.user"

    type = fields.Selection(
        selection_add=TYPE,
    )


class GitRepository(models.Model):
    _inherit = "project.git.repository"

    type = fields.Selection(
        selection_add=TYPE,
    )


class GitCommit(models.Model):
    _inherit = "project.git.commit"

    type = fields.Selection(
        selection_add=TYPE,
    )


class GitBranch(models.Model):
    _inherit = "project.git.branch"

    type = fields.Selection(
        selection_add=TYPE,
    )


class GitPayloadParser(models.AbstractModel):
    _inherit = "project.git.payload.parser"

    # -------------------------------------------
    # Header
    # -------------------------------------------
    def parse_bitbucket_header(self, type, raw_payload):
        headers = http.request.httprequest.headers
        action_type = self._map_bitbucket_action_type(headers)

        data = {
            "event": headers.get("X-Event-Key"),
            "delivery": headers.get("X-Request-UUID"),
            "action_type": action_type,
            "action": self._format_action_name(action_type),
        }

        return data

    def _map_bitbucket_action_type(self, headers):
        event = headers.get("X-Event-Key")

        if event not in self._bitbucket_supported_event_types():
            return False

        event = event.split(":")[1]
        return event

    def _format_action_name(self, action_type):
        return "git_%s" % (action_type,)

    def _bitbucket_supported_event_types(self):
        return ["repo:push"]

    # -------------------------------------------
    # Payload
    # -------------------------------------------
    def parse_bitbucket_payload(self, context):
        method_name = "parse_bitbucket_%s" % context.action_type
        parse_event_method = getattr(self, method_name)
        return parse_event_method(context)

    # -------------------------------------------
    # Action Push
    # -------------------------------------------
    def parse_bitbucket_push(self, context):
        return {
            "repository": self.parse_bitbucket_repository(context),
            "branches": self.parse_bitbucket_branches(context),
            "sender": self.parse_bitbucket_sender(context)
        }

    # -------------------------------------------
    # Action Delete
    # -------------------------------------------
    def parse_bitbucket_delete(self, context):
        return {
            "branches": self.parse_gitlab_branches(context, False)
        }

    # -------------------------------------------
    # Paring methods
    # -------------------------------------------
    def parse_bitbucket_branches(self, context, commits=True):
        branches = []
        for branch in context.raw_payload["push"]["changes"]:
            branch_data = self.parse_bitbucket_branch(context, branch, commits)
            branches.append(branch_data)
        return branches

    def parse_bitbucket_branch(self, context, branch, commits=True):
        data = {
            "name": branch["new"]["name"],
            "url": branch["new"]["links"]["html"]["href"],
            "type": context.type,
            "repository_id": context.repository.id
        }

        if commits:
            data["commits"] = self.parse_bitbucket_commits(context, branch)

        return data

    def parse_bitbucket_commits(self, context, branch):
        commits = []
        for commit in branch["commits"]:
            commits.append(self.parse_bitbucket_commit(context, commit))
        return commits

    def parse_bitbucket_commit(self, context, commit):
        from dateutil.parser import parse
        return {
            "name": commit["hash"][:8],
            "message": commit["message"],
            "url": commit["links"]["html"]["href"],
            "date": parse(commit["date"]).strftime("%Y-%m-%d %H:%M:%S"),
            "type": context.type,
            "author": self.parse_bitbucket_commit_author(context, commit),
        }

    def parse_bitbucket_commit_author(self, context, commit):
        author = commit["author"]
        user = author["user"]
        email = re.search("%s(.*)%s" % ("<", ">"), author["raw"]).group(1)
        return {
            "name": user["display_name"],
            "username": user["username"].lower(),
            "uuid": user["uuid"][1:-1],
            "avatar": user["links"]["avatar"]["href"],
            "url": user["links"]["html"]["href"],
            "email": email,
            "type": context.type,
        }

    def parse_bitbucket_sender(self, context):
        sender = context.raw_payload["actor"]
        return {
            "name": sender["display_name"],
            "username": sender["username"],
            "avatar": sender["links"]["avatar"],
            "type": context.type,
        }

    def parse_bitbucket_repository(self, context):
        repository = context.raw_payload["repository"]
        return {
            "name": repository["name"],
            "full_name": repository["full_name"],
            "uuid": repository["uuid"][1:-1],
            "url": repository["links"]["html"]["href"],
            "owner": self.parse_bitbucket_repository_owner(context),
            "type": context.type,
        }

    def parse_bitbucket_repository_owner(self, context):
        owner = context.raw_payload["repository"]["owner"]
        return {
            "name": owner["display_name"],
            "username": owner["username"].lower(),
            "uuid": owner["uuid"][1:-1],
            "avatar": owner["links"]["avatar"]["href"],
            "url": owner["links"]["html"]["href"],
            "type": context.type,
        }
