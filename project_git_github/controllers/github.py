# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

import json
import urllib.parse

from odoo import http, _
from odoo.addons.project_git.controller.controller\
    import GitController, GitContext

import logging

_logger = logging.getLogger(__name__)


class GitHubContext(GitContext):
    def __init__(self, token, payload):
        GitContext.__init__(self, 'github', token, payload)


class GitHubController(GitController):
    @http.route([
        '/github/payload/<string:token>'
    ], methods=['post'], type='http', auth='public', csrf=False)
    def process_github(self, token, *args, **kw):
        payload = json.loads(http.request.httprequest.form['payload'])
        return self.process_request(GitHubContext(token, payload))

    def validate_github_payload(self, context):

        # We need secret on one of the ends in order to validate payload
        if not context.has_signature and not context.repository.secret:
            return True

        payload = http.request.httprequest.form['payload'].encode("utf-8")
        payload = "payload=" + urllib.parse.quote_plus(payload)
        payload_valid = context.validate_payload(payload)

        if not payload_valid:
            _logger.warning(
                _("GitHub (delivery='%s'): received for repository (id='%s') "
                  "which could not be validated!.")
                % (context.delivery, context.repository.id)
            )
        return payload_valid
