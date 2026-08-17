# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError

# Token values shipped by the modules demo data: publicly known, they must
# never be used as credentials (neither inbound nor outbound).
BANNED_TOKENS = ("token",)


class ProjectGitAuth(models.AbstractModel):
    """Anchor for the platform API clients.

    Each platform bridge adds its own connection method here
    (e.g. _connect_github, _connect_gitlab) together with the python
    library it relies on: the base module stays free of git platform
    dependencies.
    """

    _name = "project.git.auth"
    _description = "Git Platform Authentication"

    @api.model
    def _get_token_param(self, key):
        token = self.env["ir.config_parameter"].sudo().get_param(key)
        if not token or token in BANNED_TOKENS:
            raise UserError(
                _(
                    "The %s system parameter is missing or still set to "
                    "the insecure demo default: configure a real API token.",
                    key,
                )
            )
        return token
