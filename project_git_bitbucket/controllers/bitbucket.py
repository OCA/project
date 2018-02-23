# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import http
from odoo.addons.project_git.controller.controller import \
    GitController, GitContext


class BitBucketContext(GitContext):
    def __init__(self, token, payload):
        GitContext.__init__(self, 'bitbucket', token, payload)


class BitBucketController(GitController):

    # Payload verification thread:
    # https://bitbucket.org/site/master/issues/12195/webhook-hmac-signature-security-issue

    @http.route([
        '/bitbucket/payload/<string:token>'
    ], type='json', auth='public', website=True)
    def process_request_bitbucket(self, token, *args, **kw):
        return self.process_request(
            BitBucketContext(token, http.request.jsonrequest)
        )
