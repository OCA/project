# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).


from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.mail import MailController


class ProjectBrowser(http.Controller):
    def get_record_url(self, model, domain):
        record = request.env[model].sudo().search(domain, limit=1)
        record_id = record and record.id or 0
        return MailController._redirect_to_record(model, record_id)

    def get_task_url(self, key):
        return self.get_record_url("project.task", [("key", "=ilike", key)])

    def get_project_url(self, key):
        return self.get_record_url("project.project", [("key", "=ilike", key)])

    @http.route(["/projects/<string:key>"], type="http", auth="user")
    def open_project(self, key, **kwargs):
        return self.get_project_url(key)

    @http.route(["/tasks/<string:key>"], type="http", auth="user")
    def open_task(self, key, **kwargs):
        return self.get_task_url(key)
