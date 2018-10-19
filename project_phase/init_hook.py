# Copyright 2018 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def post_init_hook(cr, registry):
    cr.execute("""
        UPDATE project_project
        SET phase_id = (SELECT id FROM project_phase WHERE sequence = 1)
        WHERE phase_id IS NULL;
    """)
