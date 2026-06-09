# Copyright 2026 Innovara Ltd - Manuel Fombuena
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from psycopg2 import sql

from odoo import fields, models, tools


class ProjectCostsRevenues(models.Model):
    """Read-only reporting model backed by a SQL view over timesheet
    (analytic) lines, enriched with sale-order and project data. One row per
    timesheet line; the timesheet date drives the period grouping."""

    _name = "project.costs.revenues"
    _description = "Project Costs and Revenues"
    _auto = False  # this model is a database VIEW, not a table
    _rec_name = "project_id"
    _order = "date desc"

    # --- grouping dimensions (use as pivot rows/columns) ---
    project_id = fields.Many2one("project.project", readonly=True)
    account_id = fields.Many2one(
        "account.analytic.account", string="Analytic Account", readonly=True
    )
    partner_id = fields.Many2one("res.partner", string="Customer", readonly=True)
    project_user_id = fields.Many2one(
        "res.users", string="Project Manager", readonly=True
    )
    company_id = fields.Many2one("res.company", string="Project Company", readonly=True)
    currency_id = fields.Many2one(
        "res.currency", string="Project Currency", readonly=True
    )
    product_id = fields.Many2one("product.product", readonly=True)
    sale_order_id = fields.Many2one("sale.order", readonly=True)
    so_line_id = fields.Many2one(
        "sale.order.line", string="Sale Order Line", readonly=True
    )
    date = fields.Date(readonly=True)
    so_confirmation_date = fields.Datetime(
        string="Sales Order Confirmation Date", readonly=True
    )
    # extras not present in the original report, handy for drill-down:
    task_id = fields.Many2one("project.task", readonly=True)
    employee_id = fields.Many2one("hr.employee", readonly=True)

    # --- measures ---
    timesheet_duration = fields.Float(readonly=True)
    timesheet_cost = fields.Monetary(readonly=True, currency_field="currency_id")
    amount_to_invoice = fields.Monetary(
        string="Untaxed Amount to Invoice", readonly=True, currency_field="currency_id"
    )
    amount_invoiced = fields.Monetary(
        string="Untaxed Amount Invoiced", readonly=True, currency_field="currency_id"
    )

    def init(self):
        # The analytic-account column on account.analytic.line is named
        # `account_id`; guard it so the view still builds if a given install
        # has reworked analytic plans and renamed/removed it.
        self.env.cr.execute(
            """
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'account_analytic_line'
              AND column_name = 'account_id'
            """
        )
        account_col = "aal.account_id" if self.env.cr.fetchone() else "NULL::integer"

        tools.drop_view_if_exists(self.env.cr, self._table)
        # Identifiers are composed with psycopg2.sql so the dynamic table name
        # and the (code-chosen, never user-supplied) analytic-account column
        # cannot be a SQL-injection vector.
        self.env.cr.execute(
            sql.SQL(
                """
                CREATE OR REPLACE VIEW {table} AS (
                    SELECT
                        aal.id                  AS id,
                        aal.project_id          AS project_id,
                        {account_col}           AS account_id,
                        p.partner_id            AS partner_id,
                        p.user_id               AS project_user_id,
                        p.company_id            AS company_id,
                        c.currency_id           AS currency_id,
                        sol.product_id          AS product_id,
                        sol.order_id            AS sale_order_id,
                        aal.so_line             AS so_line_id,
                        aal.task_id             AS task_id,
                        aal.employee_id         AS employee_id,
                        aal.date                AS date,
                        so.date_order           AS so_confirmation_date,
                        aal.unit_amount         AS timesheet_duration,
                        aal.amount              AS timesheet_cost,
                        CASE
                            WHEN aal.timesheet_invoice_id IS NULL
                                 AND aal.so_line IS NOT NULL
                            THEN aal.unit_amount * sol.price_unit
                                 * (1.0 - COALESCE(sol.discount, 0.0) / 100.0)
                            ELSE 0.0
                        END                     AS amount_to_invoice,
                        CASE
                            WHEN aal.timesheet_invoice_id IS NOT NULL
                                 AND aal.so_line IS NOT NULL
                            THEN aal.unit_amount * sol.price_unit
                                 * (1.0 - COALESCE(sol.discount, 0.0) / 100.0)
                            ELSE 0.0
                        END                     AS amount_invoiced
                    FROM account_analytic_line aal
                    JOIN project_project p
                        ON p.id = aal.project_id
                    LEFT JOIN res_company c
                        ON c.id = COALESCE(p.company_id, aal.company_id)
                    LEFT JOIN sale_order_line sol
                        ON sol.id = aal.so_line
                    LEFT JOIN sale_order so
                        ON so.id = sol.order_id
                    WHERE aal.project_id IS NOT NULL
                )
                """
            ).format(
                table=sql.Identifier(self._table),
                account_col=sql.SQL(account_col),
            )
        )
