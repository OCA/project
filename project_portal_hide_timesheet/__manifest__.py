{
    "name": "Project Portal Hide Timesheet",
    "version": "18.0.1.0.0",
    "depends": [
        "hr_timesheet",
        "portal",
        "sale_timesheet",
    ],
    "website": "https://github.com/OCA/project",
    "author": "PyTech SRL, Odoo Community Association (OCA)",
    "maintainers": [
        "HekkiMelody",
        "SirPyTech",
    ],
    "category": "Project",
    "license": "AGPL-3",
    "data": [
        "views/timesheet_sheet_templates.xml",
    ],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
