## Columns

| Column | Source |
|---|---|
| Timesheet Duration | timesheet hours (`unit_amount`) |
| Timesheet Cost | timesheet cost (`amount`, negative) |
| Untaxed Amount to Invoice | hours × SO line price (− discount) for time **not yet** invoiced |
| Untaxed Amount Invoiced | hours × SO line price (− discount) for time **already** invoiced |

Default pivot rows are grouped by month; add Project / Customer / Employee as
extra row or column groupings from the pivot UI (the "+" buttons).

## Assumptions / simplifications

- Revenue is the **billable value of timesheets**, so the report is meaningful
  for time-and-material / "invoice on timesheets" projects. Fixed-price or
  milestone billing won't show a meaningful "to invoice" figure here because
  that revenue isn't tied to hours.
- Service products are assumed to be **sold per hour** (timesheet hours and SO
  line price share the same unit). If you sell in days, adjust the SQL.
- **Single company currency** is assumed; SO-line price and timesheet cost are
  treated as the same currency. Add conversion in the SQL for multi-currency.
- "Invoiced" uses the same hours × price formula (not the posted invoice line
  total) so it stays consistent with "to invoice"; in most T&M cases they match.
