# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import http
from odoo.addons.project_git.controller.controller \
    import GitController, GitContext


class GitLabContext(GitContext):
    def __init__(self, token, payload):
        GitContext.__init__(self, 'gitlab', token, payload)

    @property
    def gitlab_token(self):
        return self.header['token']

    @property
    def has_gitlab_token(self):
        return 'token' in self.header


class GitLabController(GitController):

    @http.route([
        '/gitlab/payload/<string:token>'
    ], type='json', auth='public',  website=True)
    def process_request_gitlab(self, token, *args, **kw):
        return self.process_request(
            GitLabContext(token, http.request.jsonrequest)
        )

    # There is an open issue:
    # URL: https://gitlab.com/gitlab-org/gitlab-ce/issues/37380
    # for implementation of the GitHub like web hook auth.
    def validate_gitlab_payload(self, context):
        if not context.has_gitlab_token and not context.repository.secret:
            return True

        # This method is getting too silly!
        return context.gitlab_token == context.repository.secret
