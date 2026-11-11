# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Forecast Lines Holidays Public",
    "summary": "Project Forecast Lines taking public holidays into account",
    "version": "19.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "depends": [
        "project_forecast_line",
        "hr_holidays_public",
        "calendar_public_holiday",
    ],
    "data": ["views/res_config_settings_views.xml"],
    "development_status": "Alpha",
    "installable": True,
}
