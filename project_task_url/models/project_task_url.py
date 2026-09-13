# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from werkzeug import urls

from odoo import api, fields, models


class ProjectTaskUrl(models.Model):
    _name = "project.task.url"
    _description = "Project Task Url"

    name = fields.Char()
    url_link = fields.Char()
    task_id = fields.Many2one("project.task")

    def _clean_url_link(self, url_link):
        url = urls.url_parse(url_link)
        if not url.scheme:
            if not url.netloc:
                url = url.replace(netloc=url.path, path="")
            url_link = url.replace(scheme="http").to_url()
        return url_link

    def write(self, vals):
        if vals.get("url_link"):
            vals["url_link"] = self._clean_url_link(vals["url_link"])
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("url_link"):
                vals["url_link"] = self._clean_url_link(vals["url_link"])
        return super().create(vals_list)
