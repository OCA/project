# Copyright 2019-2020 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        # This is moved here to prevent dependency to this module
        # (e.g. in project_timeline)
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if view_type == "form":
            doc = etree.XML(res["arch"])
            target = doc.xpath("//group[@name='extra_settings']")
            if target:
                target = target[0]
                if not doc.xpath("//field[@name='date_start']"):
                    target.append(doc.makeelement("field", {"name": "date_start"}))
                if not doc.xpath("//field[@name='date']"):
                    target.append(doc.makeelement("field", {"name": "date"}))
                res["arch"] = etree.tostring(doc, encoding="unicode")
        return res
