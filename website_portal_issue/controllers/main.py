# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm


class WebsiteForm(WebsiteForm):
    # Check and insert values from the form on the model <model>

    @http.route(
        '/website_form/<string:model_name>',
        type='http', auth="user",
        methods=['POST'],
        website=True
        )
    def website_form(self, model_name, **kwargs):
        if model_name == 'project.issue' and not request.params.get('state'):
            pass
        return super(WebsiteForm, self).website_form(model_name, **kwargs)

    @http.route(['/issue/new'], type='http', auth="user", website=True)
    def issue(self, country=None, department=None, office_id=None, **kwargs):
        projects = request.env['project.project'].search([
            ('privacy_visibility', '=', 'portal'), ('use_issues', '=', True)
            ])
        # Render page
        return request.render("website_portal_issue.new-issue", {
            "project_filters": projects
            })
    # Redirect to success page

    @http.route("/issue-thank-you", type="http", auth="user", website=True)
    def issue_tank_you(self, **kw):
        return request.render("website_portal_issue.issue-thank-you")
