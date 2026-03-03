This module does not require additional configuration after installation. It works automatically once installed.

## Installation

1. Go to the **Apps** menu
2. Remove the "Apps" filter if necessary
3. Search for "Project Update Portal Access"
4. Click **Install**

## Prerequisites

Make sure the following modules are installed:
* **Project** (base project module)
* **Portal** (Odoo's portal module for customer access)

The system will automatically install the necessary dependencies during installation.

## Permissions

The module uses portal access rules to control visibility:
* Portal users can view updates if they are followers of the project
* Portal users can view updates if they are followers of the specific update
* Access is read-only for portal users (no create, write, or delete permissions)

## Access Configuration

**Adding Followers to Projects**

1. Go to the **Projects** module
2. Open a project
3. In the project form, add followers in the **Followers** field
4. Followers will automatically have access to project updates via portal

**Adding Followers to Updates**

1. When creating or editing a project update
2. Add followers in the **Followers** field of the update
3. Those followers will have access to that specific update via portal

No additional permission configuration is required.

