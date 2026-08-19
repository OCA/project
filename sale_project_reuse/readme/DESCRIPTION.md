Standard Odoo creates a brand new project for every sales order selling a
service that tracks a project, and there is no place to record which project
belongs to a customer.

This module adds that notion:

- a *Reuse Project* field on the customer, holding the project to reuse,
- a *Reuse Project* flag on the product,
- when a flagged product is added to a sales order, the customer's project is
  proposed as the project of that order,
- confirming that order creates the tasks in the project of the order instead
  of generating a new one,
- when the customer has no project yet, the project of the first confirmed
  sales order is stored on the customer, so the following orders reuse it.
