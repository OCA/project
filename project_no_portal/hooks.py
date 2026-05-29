# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    # Flip projects set to portal visibility before the constraint can reject
    # writes, but only for companies that block portal access.
    portal_projects = env["project.project"].search(
        [("privacy_visibility", "=", "portal")]
    )
    to_flip = portal_projects.filtered(
        lambda project: (project.company_id or env.company).block_project_portal_access
    )
    if to_flip:
        _logger.info(
            "project_no_portal: switching %s project(s) from portal to employees",
            len(to_flip),
        )
        to_flip.write({"privacy_visibility": "employees"})

    enabled = bool(
        env["res.company"].search_count(
            [("block_project_portal_access", "=", False)], limit=1
        )
    )
    env["project.task"]._set_share_task_action(enabled)
    env["project.project"]._set_share_project_action(enabled)


def uninstall_hook(env):
    # Restore the core action state: "Share Task" was a cog action in core
    # (binding restored); "Share Project" had no binding in core (left unbound).
    env["project.task"]._set_share_task_action(True)
    env["project.project"]._set_share_project_action(False)
