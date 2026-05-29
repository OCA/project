# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ProjectTask(models.Model):
    _name = "project.task"
    _inherit = ["project.task", "project.portal.block.mixin"]

    # Exposed on the kanban card to hide the "Share Task" link, which links the
    # share action directly by xml-id and thus bypasses the action-binding removal.
    portal_share_blocked = fields.Boolean(compute="_compute_portal_share_blocked")

    def _compute_portal_share_blocked(self):
        for task in self:
            company = task._portal_block_company()
            task.portal_share_blocked = company.block_project_portal_access

    def _set_share_task_action(self, enabled):
        """
        Toggle the "Share Task" action, which opens portal.share.wizard
        """
        action = self.env.ref("project.portal_share_action", raise_if_not_found=False)
        if not action:
            return
        model = self.env.ref("project.model_project_task")
        action.binding_model_id = model.id if enabled else False
