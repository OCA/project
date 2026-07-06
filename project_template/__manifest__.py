# Copyright 2019 Patrick Wilson <patrickraymondwilson@gmail.com>
# Copyright 2026 ACSONE SA/NV
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

{
    "name": "Project Templates",
    "summary": """Project Templates""",
    "author": "Patrick Wilson, ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "category": "Project Management",
    "version": "18.0.1.0.1",
    "license": "AGPL-3",
    "depends": [
        # Odoo Community
        "project",
    ],
    "data": ["views/project.xml", "views/project_task.xml"],
    "application": False,
    "development_status": "Beta",
    "maintainers": ["patrickrwilson", "sbejaoui"],
}
