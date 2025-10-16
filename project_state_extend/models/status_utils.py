# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.project.models.project_update import STATUS_COLOR

NATIVE_PROJECT_STATUS_SELECTION = [
    ("on_track", "On Track"),
    ("at_risk", "At Risk"),
    ("off_track", "Off Track"),
    ("on_hold", "On Hold"),
    ("to_define", "Set Status"),
]

NATIVE_UPDATE_STATUS_SELECTION = [
    ("on_track", "On Track"),
    ("at_risk", "At Risk"),
    ("off_track", "Off Track"),
    ("on_hold", "On Hold"),
]

NATIVE_STATUS_KEYS = {key for key in STATUS_COLOR if isinstance(key, str)}


def get_extended_status_selection(env, native_states):
    custom_states = (
        env["project.state.extend"]
        .with_context(active_test=False)
        .search([], order="sequence, id")
    )
    return native_states + [
        (state.technical_name, state.name) for state in custom_states
    ]


def get_extended_status_color(env):
    custom_states = (
        env["project.state.extend"].with_context(active_test=False).search([])
    )
    extended_status_color = STATUS_COLOR.copy()
    for state in custom_states:
        extended_status_color[state.technical_name] = state.color
    return extended_status_color
