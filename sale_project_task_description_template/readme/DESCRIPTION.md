This module extends the Project Task Description Template and integrates it with Sales and Projects.
When tasks are generated from sales order lines, the task will automatically use the Task Description Template
defined on the related product.

Optionally, you can include key information from the sales order line (like product name and quantity) above
the template, providing more context directly in the task description.

Key Features:
- New field on product: assign a Task Description Template for service products with Service Tracking set to 'Task' or 'Project & Task'.
- Optional boolean to include the sale order line info in the task description.
- Automatic application of the template (and optionally the sales line info) when creating tasks from sales orders.
