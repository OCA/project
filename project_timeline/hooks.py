# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def uninstall_hook(cr, _):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _clean_action_view_mode_timeline(env)


def _clean_action_view_mode_timeline(env):
    models = ["project.project", "project.task", "report.project.task.user"]
    domain = [
        ("view_mode", "ilike", "timeline"),
        ("res_model", "in", models),
    ]
    Action = env["ir.actions.act_window"]
    for action in Action.search(domain):
        view_mode = [
            m for m in action.view_mode.split(",") if m.lower().strip() != "timeline"
        ]
        # If 'view_mode' is now empty: unlink related menus and the action
        if not view_mode:
            _unlink_action(env, action)
        else:
            action.view_mode = ",".join(view_mode)


def _unlink_action(env, action):
    env["ir.ui.menu"].search(
        [("action", "=", "ir.actions.act_window,%d" % action.id)]
    ).unlink()
    action.unlink()
