This module adds a per-company switch **Restrict task-to-ticket conversion to
portal projects** under Settings > Project.

When enabled for a company, converting a task into a helpdesk ticket
(`Convert to Ticket` action) is only allowed when the task's project privacy is
set to *Invited portal users …* (`privacy_visibility = 'portal'`). Any other
task raises an error instead of opening the conversion wizard.

This prevents leaking a non-portal task's data through a helpdesk ticket's
public share link.

The switch is off by default (standard Odoo behaviour), scoped per company
(multi-company friendly), and independent of any portal-blocking module.
