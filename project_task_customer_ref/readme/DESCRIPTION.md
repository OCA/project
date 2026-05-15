Adds an **Order Customer Reference** field (`customer_reference`) to
`project.task` so that customer PO/requisition numbers are visible on
tasks, capturable via website webforms, and kept in sync with the linked
sale order.

Features:

- **Task field**: `customer_reference` (Char, not copied on duplication)
  is added to the task form view and list view (hidden by default,
  toggleable via the optional-columns menu).
- **Auto-populated from sale order**: when a task is created automatically
  from a confirmed sale order (service lines with `service_tracking`),
  the task inherits the SO's `client_order_ref` as its
  `customer_reference`.
- **Propagation back to sale order**: when `customer_reference` is set or
  updated on a task, it is written to `client_order_ref` on the linked
  sale order — but only if that field is currently empty, preventing
  unintended overwrites.
- **Website webform support**: the field is whitelisted for the website form
  builder so it appears in the field picker when configuring a webform that
  creates `project.task` records.
