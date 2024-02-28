Odoo has a feature called "Project Sharing" that allows portal users to view a project's
kanban, which has functionalities similar to the backend system.

There's a preset list of fields that portal users can access, which is harcoded in the
module's source code.

That's nice but inconvinient if a user introduces new fields to the form and wants to
share these with the portal users. They can't currently do this without using a Python
override.

To resolve this, the module lets users whitelist these custom fields directly through
the ``ir.model.field`` model.
