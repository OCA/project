# Copyright 2018 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Project Phase",
    "version": "11.0.1.1.0",
    "category": "Project",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
    ],
    "depends": [
        "project",
    ],
    "data": [
        "data/project_phase_data.xml",
        "security/ir.model.access.csv",
        "views/project_project_view.xml",
        "views/project_phase_view.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
