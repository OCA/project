# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

import re
import json
import logging
from abc import ABCMeta

from odoo import http

from ..utils.utils import hmac_new, digest_compare

_logger = logging.getLogger(__name__)


class GitContext(object):
    __metaclass__ = ABCMeta

    def __init__(self, type, token, raw_payload):
        self._request = http.request
        self._type = type
        self._token = token
        self._raw_payload = raw_payload
        self._repository = False

        self._header = False
        self._payload = False

    @property
    def request(self):
        return self._request

    @property
    def env(self):
        return self._request.env

    @property
    def type(self):
        return self._type

    @property
    def token(self):
        return self._token

    @property
    def repository(self):
        return self._repository

    @repository.setter
    def repository(self, repository):
        self._repository = repository

    @property
    def parser(self):
        return self.env['project.git.payload.parser']

    @property
    def header(self):
        if not self._header:
            self._header = self.parser.parse_header(self)
        return self._header

    @property
    def signature(self):
        return self.header['signature']

    @property
    def has_signature(self):
        return 'signature' in self.header

    @property
    def delivery(self):
        return self.header['delivery']

    @property
    def raw_payload(self):
        return self._raw_payload

    @property
    def payload(self):
        if not self._payload:
            self._payload = self.parser.parse(self)
        return self._payload

    @property
    def action_type(self):
        return self.header['action_type']

    @property
    def has_action(self):
        return self.header['action_type']

    @property
    def action(self):
        return self.header['action']

    def validate_payload(self, payload):
        payload_digest = hmac_new(self.repository.secret, payload, True)
        return digest_compare(payload_digest, self.signature)

    def not_found(self):
        if isinstance(self._request, http.HttpRequest):
            return self._request.not_found()

        return json.dumps({"response": "Not found!"})

    def render(self, template_xml_id, values):
        return self.env.ref(template_xml_id).render(values)

    def render_task_subject(self, values):
        return self.render(
            'project_git.task_code_committed_notification_subject', values
        )

    def render_task_body(self, values):
        return self.render(
            'project_git.task_code_committed_notification_body', values
        )

    def render_orphan_subject(self, values):
        return self.render(
            'project_git.orphan_code_committed_notification_subject', values
        )

    def render_orphan_body(self, values):
        return self.render(
            'project_git.orphan_code_committed_notification_body', values
        )


class GitController(http.Controller):

    def process_request(self, context):
        repository = context.env["project.git.repository"].sudo().search([
            ("type", "=", context.type),
            ("odoo_uuid", "=", context.token),
        ], limit=1)

        if not repository:
            return context.not_found()

        context.repository = repository

        if not self.validate_payload(context):
            return context.not_found()

        return getattr(self, context.action)(context)

    def find_repository(self, context):
        repositories = context.env["project.git.repository"].sudo().search([
            ("type", "=", context.type)
        ])
        for repository in repositories:
            if context.token_match(repository):
                return repository
        return False

    def validate_payload(self, context):
        if not (context.has_action and context.repository.project_id):
            return False

        validation_method_name = "validate_%s_payload" % context.type
        if hasattr(self, validation_method_name):
            return getattr(self, validation_method_name)(context)

        return True

    def reponse_ok(self):
        return "OK"

    def reponse_nok(self):
        return "NOK"

    def git_ping(self, context):
        return "PONG"

    def git_delete(self, context):
        for branch_data in context.payload['branches']:
            branch = context.env["project.git.branch"].sudo().search([
                ("name", "=", branch_data["name"]),
                ("repository_id", "=", branch_data["repository_id"]),
                ("type", "=", branch_data["type"])
            ], limit=1)

            if branch:
                branch.unlink()
        return self.reponse_ok()

    def compile_task_key_pattern(self, context):
        pattern = context.repository.project_id.key + " ?-? ?[0-9]+"
        return re.compile(pattern, re.IGNORECASE)

    def git_push(self, context):
        try:
            GitUser = context.env["project.git.user"].sudo()
            ResUser = context.env['res.users'].sudo()

            # ============================================================
            # UPDATE/CREATE Repository owner
            # ------------------------------------------------------------

            try:
                payload = context.payload
            except Exception as ex:
                import traceback
                _logger.error(
                    "Something went wrong while parsing "
                    "repository web hook payload "
                    "(repository_id='%s', type='%s', delivery='%s'): %s"
                    "\n stack_trace:%s" % (
                        context.repository.id, context.type, context.delivery,
                        str(ex), traceback.format_exc()
                    )
                )
                return self.reponse_nok()

            repository_data = payload['repository']

            repository_owner_data = repository_data.pop("owner")

            if 'email' in repository_owner_data:
                repository_owner_user = ResUser.search(
                    [("email", "=", repository_owner_data["email"])], limit=1
                )
                repository_owner_data['user_id'] = \
                    repository_owner_user and repository_owner_user.id or False

            repository_owner = GitUser.search([
                ("username", '=', repository_owner_data["username"]),
                ("type", "=", repository_owner_data['type'])
            ], limit=1)

            if repository_owner:
                repository_owner.write(repository_owner_data)
            else:
                repository_owner = GitUser.create(repository_owner_data)
            # -----------------------------------------------------------

            # ==========================================================
            # UPDATE/CREATE Repository
            # ----------------------------------------------------------
            repository_data = context.payload['repository']
            repository_data["user_id"] = repository_owner.id
            context.repository.sudo().write(repository_data)
            # ----------------------------------------------------------

            task_commits = {}
            orphan_commits = []

            # ==========================================================
            # UPDATE/CREATE Branch
            # ----------------------------------------------------------
            for branch_data in context.payload['branches']:
                self.process_branch(branch_data,
                                    task_commits,
                                    orphan_commits,
                                    context)

            # CREATE email notification for every affected task
            sender = context.payload['sender']
            sender = GitUser.search([
                ("username", "=", sender["username"])
            ], limit=1)

            if len(task_commits):
                self.send_task_commits(task_commits, sender, context)

            if len(orphan_commits):
                self.send_orphan_commits(orphan_commits, sender, context)

            return self.reponse_ok()
        except BaseException as ex:
            import traceback
            _logger.error(
                "Something went wrong while processing repository web hook "
                "(repository_id='%s', type='%s', delivery='%s'): %s"
                "\n stack_trace:%s" % (
                    context.repository.id, context.type, context.delivery,
                    str(ex), traceback.format_exc()
                )
            )
            return self.reponse_nok()

    def process_branch(self, branch_data, task_commits, orphan_commits,
                       context):

        def sanitize_key(key):
            key = key.upper()
            pk_len = len(context.repository.project_id.key)
            key = key.replace(" ", "")
            if key[pk_len] != '-':
                key = key[:pk_len] + '-' + key[pk_len:]
            return key

        def find_task_keys(pattern, message):
            task_keys = []
            for key in re.findall(pattern, message):
                task_keys.append(sanitize_key(key))
            return task_keys

        GitBranch = context.env["project.git.branch"].sudo()
        GitCommit = context.env["project.git.commit"].sudo()
        ProjectTask = context.env["project.task"].sudo()
        GitUser = context.env["project.git.user"].sudo()
        ResUser = context.env['res.users'].sudo()

        # Preparing regular expression used to search for task keys
        # inside of commit message
        task_key_pattern = self.compile_task_key_pattern(context)

        commits = branch_data.pop('commits')

        branch = GitBranch.search([
            ("name", '=', branch_data["name"]),
            ("repository_id", "=", branch_data["repository_id"]),
            ("type", "=", branch_data["type"])
        ], limit=1)

        if branch:
            branch.write(branch_data)
        else:
            branch = GitBranch.create(branch_data)

        for commit_data in commits:
            task_keys = find_task_keys(
                task_key_pattern, commit_data["message"]
            )
            tasks = len(task_keys) and ProjectTask.search([
                ("key", "in", task_keys)
            ]) or []

            # ----------------------------------------------------
            # UPDATE/CREATE Commit Author
            # ----------------------------------------------------
            commit_author_data = commit_data.pop('author')
            commit_author = GitUser.search([
                ("email", '=', commit_author_data["email"]),
                ("type", "=", commit_author_data["type"])
            ], limit=1)

            author_user = ResUser.search([
                ('email', '=', commit_author_data["email"])
            ], limit=1)
            if author_user:
                commit_author["user_id"] = author_user.id

            if commit_author:
                commit_author.write(commit_author_data)
            else:
                commit_author = GitUser.create(commit_author_data)
            # ----------------------------------------------------

            commit_data["branch_id"] = branch.id
            commit_data["author_id"] = commit_author.id
            commit_data["task_ids"] = \
                len(tasks) and [(6, 0, tasks.ids)] or []

            commit = GitCommit.search([
                ("name", '=', commit_data["name"]),
                ("type", "=", commit_data["type"])
            ], limit=1)

            if commit:
                commit.write(commit_data)
            else:
                commit = GitCommit.create(commit_data)

            if commit.is_orphan():
                orphan_commits.append(commit)
            else:
                for task in tasks:
                    item = task_commits.get(
                        task.id, {'task': task, 'commits': []}
                    )
                    item['commits'].append(commit)
                    task_commits[task.id] = item

    def send_task_commits(self, task_commits, sender, context):
        values = {
            "context": context,
            "sender": sender,
        }

        subtype = context.env.ref("project_git.mt_task_code_committed").id
        author = sender.user_id and sender.user_id.partner_id.id or False
        email_from = "%s <%s>" % (sender.name, sender.email)

        for item in task_commits.values():
            task = item['task']
            commits = item['commits']

            values['task'] = task
            values['commits'] = commits

            subject = context.render_task_subject(values)
            body = context.render_task_body(values)

            task.message_post(
                subject=subject,
                body=body,
                subtype_id=subtype,
                author_id=author,
                email_from=email_from,
            )

    def send_orphan_commits(self, orphan_commits, sender, context):
        values = {
            "context": context,
            "sender": sender,
            'commits': orphan_commits,
        }

        author = sender.user_id and sender.user_id.partner_id.id or False
        email_from = "%s <%s>" % (sender.name, sender.email)
        subtype = context.env.ref("project_git.mt_project_code_committed").id
        subject = context.render_orphan_subject(values)
        body = context.render_orphan_body(values)

        context.repository.project_id.message_post(
            subject=subject,
            body=body,
            subtype_id=subtype,
            author_id=author,
            email_from=email_from,
        )
