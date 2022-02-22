To configure this module, you need to:

#. Go to *Inventory -> Configuration -> Settings* and check "Storage Locations" option.
#. Go to *Inventory -> Configuration -> Operation types*.
#. Create a new operation type with the following options:
    * `Operation type`: Task material
    * `Code`: TM
    * `Type of operation`: Delivery
    * `Default Source Location`: WH/Stock
    * `Default Destination Location`: WH/Stock/Shelf 1
#. Go to *Project -> Configuration -> Projects*.
#. Create a new project with the following options:
    * `Name`: Task material
    * `Operation type`: Task material
#. Go to *Project -> Configuration -> Stages* and edit some records.
    * `In progress`: Check Use Stock Moves option and add the created project.
    * `Done`: Check Use Stock Moves option + Lock Stock Moves and add the created project.
