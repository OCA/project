# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Project Revenue Recognition",
    "summary": "Add Revenue Recognition on Project",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "depends": ["account", "sale_project", "web_widget_x2many_2d_matrix"],
    "data": [
        "data/sequence.xml",
        "security/ir.model.access.csv",
        "security/project_revenue_recognition.xml",
        "views/res_config_settings_views.xml",
        "views/project_revenue_recognition_view.xml",
        "views/account_move_views.xml",
    ],
    "maintainers": ["Saran440"],
}
