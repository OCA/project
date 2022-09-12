# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Forecast Lines Bokeh Chart",
    "summary": "Project Forecast Lines Bokeh Chart",
    "version": "15.0.1.0.2",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "depends": ["project_forecast_line", "web_widget_bokeh_chart"],
    "data": [
        "security/ir.model.access.csv",
        "report/forecast_line_reporting_views.xml",
    ],
    "development_status": "Alpha",
    "installable": True,
}
