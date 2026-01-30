**1. Configure the default profitability threshold**
- Go to Settings > Project > Set the default threshold percentage
![screenshot.png](../static/description/screenshot.png)

**2. Configure a project-specific threshold (optional)**
- Go to Project > Open a project > Manage notifications section > Define a specific threshold for this project.
If no value is defined, the system will automatically use the global default threshold. (see screenshot below)

**3. Manage notification recipients**
- Define a Project Manager and followers (subscribers) for the project
These users will receive notifications when the threshold is reached.

**4. User notification preferences**
- Go to Settings > Open a user > Configure the user’s notification preferences.
![screenshot1.png](../static/description/screenshot1.png)

**5. Project notification preferences**

When project costs exceed the configured percentage of revenues, the system automatically sends (via a cron)
- An email to manager and internal user followers if the Force Email Notification option is enabled from the project.
- An activity of type To-Do for the project manager if the Create Activity option is enabled from the project.

![screenshot2.png](../static/description/screenshot2.png)
