# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        if (
            view_type == "kanban"
            and view_id
            == self.env.ref("project.project_sharing_project_task_view_kanban").id
            and not self.env.context.get("draggable")
        ):
            doc = etree.XML(result["arch"])
            nodes = doc.xpath("//kanban")
            if nodes:
                nodes[0].set("records_draggable", "0")
                nodes[0].set("create", "0")
            result["arch"] = etree.tostring(doc, encoding="unicode")
        if (
            view_type == "form"
            and view_id
            == self.env.ref("project.project_sharing_project_task_view_form").id
            and not self.env.context.get("draggable")
        ):
            doc = etree.XML(result["arch"])
            nodes = doc.xpath("//form")
            if nodes:
                nodes[0].set("edit", "0")
                nodes[0].set("create", "0")
            result["arch"] = etree.tostring(doc, encoding="unicode")
        if (
            view_type == "tree"
            and view_id
            == self.env.ref("project.project_sharing_project_task_view_tree").id
            and not self.env.context.get("draggable")
        ):
            doc = etree.XML(result["arch"])
            nodes = doc.xpath("//tree")
            if nodes:
                nodes[0].set("edit", "0")
                nodes[0].set("create", "0")
            result["arch"] = etree.tostring(doc, encoding="unicode")
        return result
