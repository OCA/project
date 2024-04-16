# Copyright 2024 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Forecast Line Priority",
    "summary": "Project Forecast Line dates according to task priority",
    "version": "14.0.1.0.0",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "maintainers": ["ntsirintanis"],
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "depends": ["project_forecast_line_deadline", "project_task_add_very_high"],
    "data": [
        "data/ir_actions_server.xml",
        "views/res_config_settings.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
}
