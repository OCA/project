# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Business Requirement Deliverable Category",
    'category': 'Business Requirements Management',
    'summary': 'Business Requirement Deliverable Task Categories',
    "version": "8.0.1.0.0",
    "website": "www.elico-corp.com",
    "author": "Elico corp",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "business_requirement_deliverable",
        "business_requirement_project",
        "project_task_category",
    ],
    "data": [
        "views/business_requirement_deliverable_categ.xml",
    ],
}
