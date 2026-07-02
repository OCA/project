# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import functools

from odoo import models
from odoo.osv import expression


class ProjectPortalBlockMixin(models.AbstractModel):
    _name = "project.portal.block.mixin"
    _description = "Deny portal users access for companies that block it"

    def _portal_block_restricted_user(self):
        # Only portal users (outside superuser mode) are subject to the block.
        return not self.env.su and self.env.user._is_portal()

    def _portal_block_company(self):
        # A record with no company falls back to the current company.
        self.ensure_one()
        return self.company_id or self.env.company

    def _portal_block_search_domain(self, domain):
        if not self._portal_block_restricted_user():
            return domain
        keep = [("company_id.block_project_portal_access", "=", False)]
        # company_id is False -> falls back to the current company.
        if not self.env.company.block_project_portal_access:
            keep = ["|", ("company_id", "=", False)] + keep
        domain = expression.AND([domain, keep])
        return domain

    def _search(self, domain, offset=0, limit=None, order=None):
        domain = self._portal_block_search_domain(domain)
        return super()._search(domain, offset=offset, limit=limit, order=order)

    def _check_access(self, operation):
        result = super()._check_access(operation)
        if result is not None or not self._portal_block_restricted_user():
            return result
        forbidden = self.filtered(
            lambda record: record._portal_block_company().block_project_portal_access
        )
        if not forbidden:
            return result
        return forbidden, functools.partial(
            self.env["ir.rule"]._make_access_error, operation, forbidden
        )
