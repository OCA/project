def uninstall_hook(cr, registry):
    # Convert priority from very high to high to avoid inconsistency
    # after the module is uninstalled
    cr.execute(
        "UPDATE project_task SET priority = '1' WHERE priority like '2'"
    )
