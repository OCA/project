1. In *Sales > Products* when creating a product of Service type, in *Invoicing > Invoicing policy* you can now use an extra *track service* named 'Create a project and link tasks'.
    > Note : the existing *track services* are preserved and can still be used together with the following options, the new service was created in order not to track hours as delivered in sale order. As a remainder for the existing types:
    > - Manual : delivered quantities are manually set on sale order line
    > - Timesheet : hours spent on project with the same customer are reported in the sale order as delivered quantities
    > - Task : Create a task in a specific project (if filled) and reports hours from this task in delivered quantities

    Now you can add project and task type for this product.

    - If you select none, when creating a project from sale order, a wizard will propose you to select an existing project or to create a new one and a task will be created inside that project with the content of your sale order line description.
    - If you select a project and a task type, when creating a project from sale order, a new task with the content of the sale order line description will be created inside the defined project with defined task type.

2. In *Sales > Configuration > Settings* you can now configure the default task type / stage you want to use when creating task associated to a sale order line.

3. In *Project > Configuration > Stages* a new boolean field case_default / Default step has been added to each stage to define which stages should be added by default to any new project.

4. In *Project > Configuration > Configuration* your can configure:
    - an *alias prefix* has been added so that new projects will have an e-mail alias prefixed with this field
    - the *number of hours worked per day* and *the price of one person day* in order to derivate from amount in sale order the number of hours to assign to each project / task
