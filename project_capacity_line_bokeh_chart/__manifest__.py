# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Project Capacity Lines Bokeh Chart",
    "summary": "Project Capacity Lines Bokeh Chart",
    "version": "15.0.1.0.0",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Project",
    "website": "https://github.com/OCA/project",
    "depends": ["project_capacity_line", "web_widget_bokeh_chart"],
    "data": [
        "security/ir.model.access.csv",  # TO FIX
        "report/capacity_line_reporting_views.xml",
    ],
    "installable": True,
}
