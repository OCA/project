This module adds seniority levels that can be assigned to employees and products.

When an employee timesheets on a specific project this module will checks the project configuration.
It looks for an existing mapping for the employee and a sale order line (in the invoicing tab).
If no mapping are found one will be automatically created with the first sale order line with the seniority level that corresponds with the seniority level of the employee.
If no sale order line fits that criteria one will be created with any product with the correct seniority level and an action for the salesman will be created.
