1. **Go to the desired project**, click the three dots (⋯) in the top-right corner, and select **Settings**.
2. A new section named **FTE** will appear in the project form.
3. Click the **Generate FTE Lines** button to open the wizard.

### 🔧 In the wizard:

- Select the **Start Date**. This date will be stored on the project.
- **total FTE hours** will be calculated from the total of the allocated_hours of the tasks.
- Fill in the **Monthly Hours** manually. These represent the typical number of hours to distribute per month, and are used to calculate the duration.
- Define the **Profile Distribution** by selecting the roles and specifying the number of hours per role.

> 💡 If your roles have a **Price per Hour** defined (on the role itself), the wizard will use it to compute the cost of each role’s hours.

- The wizard will automatically compute:
  - The **percentage** of each role's hours,
  - The **Monthly Amount** and **Total Amount**,
  - The **End Date**, based on the total hours and monthly distribution.

---

### 🎯 Autofill from Milestones

Instead of filling the profile distribution manually, you can click **Load from Milestones**:

- This will gather all project tasks linked to milestones,
- And group their allocated hours by the **role assigned to each milestone**,
- Creating a profile distribution automatically.

This is useful when project planning has already been done using milestones.

---

### 📆 Generating the Lines

Once all fields are filled:

1. Click **Generate**.
2. FTE lines will be created month by month from the selected Start Date to the computed End Date.
3. The hours and costs are distributed according to the profile distribution.

---
