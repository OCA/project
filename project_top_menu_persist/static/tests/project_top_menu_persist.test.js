/* Copyright 2026 OBS Solutions B.V.
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {animationFrame, runAllTimers} from "@odoo/hoot-mock";
import {beforeEach, describe, expect, test} from "@odoo/hoot";
import {
    contains,
    defineActions,
    defineModels,
    fields,
    getService,
    models,
    mountWithCleanup,
    onRpc,
} from "@web/../tests/web_test_helpers";
import {WebClient} from "@web/webclient/webclient";
import {browser} from "@web/core/browser/browser";
import {defineMailModels} from "@mail/../tests/mail_test_helpers";
import {user} from "@web/core/user";

describe.current.tags("desktop");

class ProjectTask extends models.Model {
    _name = "project.task";

    name = fields.Char();

    _records = [{id: 1, name: "Task"}];
    _views = {
        kanban: `
            <kanban>
                <templates>
                    <t t-name="card"><field name="name"/></t>
                </templates>
            </kanban>`,
        search: `<search/>`,
    };
}

class Partner extends models.Model {
    name = fields.Char();

    _records = [{id: 1, name: "Partner"}];
    _views = {
        kanban: `
            <kanban>
                <templates>
                    <t t-name="card"><field name="name"/></t>
                </templates>
            </kanban>`,
        search: `<search/>`,
    };
}

class IrActionsAct_Window extends models.ServerModel {
    _name = "ir.actions.act_window";

    _records = [{id: 1}, {id: 2}, {id: 5}];
}

defineMailModels();
defineModels([ProjectTask, Partner, IrActionsAct_Window]);

defineActions([
    {
        id: 1,
        xml_id: "project_tasks",
        name: "Tasks",
        res_model: "project.task",
        views: [[false, "kanban"]],
    },
    {
        id: 2,
        xml_id: "sale_orders",
        name: "Sales Orders",
        res_model: "partner",
        views: [[false, "kanban"]],
    },
    {
        id: 3,
        name: "Sales Orders",
        type: "ir.embedded.actions",
        parent_res_model: "project.project",
        parent_action_id: 1,
        action_id: 2,
    },
    {
        id: 4,
        name: "Invoices",
        type: "ir.embedded.actions",
        parent_res_model: "project.project",
        parent_action_id: 1,
        action_id: 2,
    },
    {
        id: 5,
        xml_id: "partners",
        name: "Partners",
        res_model: "partner",
        views: [[false, "kanban"]],
    },
    {
        id: 6,
        name: "Other",
        type: "ir.embedded.actions",
        parent_res_model: "partner",
        parent_action_id: 5,
        action_id: 2,
    },
]);

beforeEach(() => {
    user.updateUserSettings("id", 1);
    user.updateUserSettings("embedded_actions_config_ids", {});
    onRpc("res.users.settings", "set_embedded_actions_setting", ({args}) => {
        const [, actionId, resId, vals] = args;
        // The model is required on the setting record.
        expect.step(`setting ${actionId}+${resId || ""} ${vals.res_model}`);
        return true;
    });
});

async function openProject(projectId) {
    await getService("action").doAction(1, {
        additionalContext: {active_id: projectId},
        clearBreadcrumbs: true,
    });
    await runAllTimers();
    await animationFrame();
}

const topMenuButtons = ".o_embedded_actions > button:not([name='openEmbeddedActions'])";

function queryTexts() {
    return [...document.querySelectorAll(topMenuButtons)].map((el) =>
        el.textContent.trim()
    );
}

async function toggleTopMenu() {
    await contains(".o_control_panel_navigation > button > i.fa-sliders").click();
    // Let the top menu fade out.
    await runAllTimers();
    await animationFrame();
}

async function toggleButton(name) {
    await contains(".o_embedded_actions [name='openEmbeddedActions']").click();
    await contains(
        `.o_popover.dropdown-menu .dropdown-item span:contains('${name}')`
    ).click();
}

test("the top menu of a project is shown by default", async () => {
    await mountWithCleanup(WebClient);
    await openProject(1);
    expect(".o_embedded_actions").toHaveCount(1);
    expect(topMenuButtons).toHaveText("Tasks");
    // The button dropdown is not opened on its own.
    expect(".o_popover.dropdown-menu").toHaveCount(0);
});

test("the top menu of another model keeps the standard behaviour", async () => {
    await mountWithCleanup(WebClient);
    await getService("action").doAction(5);
    await runAllTimers();
    expect(".o_embedded_actions").toHaveCount(0);
});

test("the buttons turned on are shown on the next project", async () => {
    await mountWithCleanup(WebClient);
    await openProject(1);
    await toggleButton("Invoices");
    expect(queryTexts()).toEqual(["Tasks", "Invoices"]);
    expect.verifySteps(["setting 1+1 project.project"]);

    await openProject(2);
    expect(queryTexts()).toEqual(["Tasks", "Invoices"]);

    await toggleButton("Tasks");
    expect.verifySteps(["setting 1+2 project.project"]);
    await openProject(1);
    expect(queryTexts()).toEqual(["Invoices"]);
});

test("a hidden top menu stays hidden on the next project", async () => {
    await mountWithCleanup(WebClient);
    await openProject(1);
    await toggleTopMenu();
    expect(".o_embedded_actions").toHaveCount(0);
    expect.verifySteps(["setting 1+1 project.project"]);

    await openProject(2);
    expect(".o_embedded_actions").toHaveCount(0);

    await toggleTopMenu();
    expect.verifySteps(["setting 1+2 project.project"]);
    await openProject(3);
    expect(".o_embedded_actions").toHaveCount(1);
});

test("a stored button that the project does not have is ignored", async () => {
    browser.localStorage.setItem(
        `project_top_menu_active_buttons:${user.userId}`,
        JSON.stringify({999: true, 3: true})
    );
    await mountWithCleanup(WebClient);
    await openProject(1);
    expect(queryTexts()).toEqual(["Tasks", "Sales Orders"]);
});

test("unreadable stored values fall back to the default", async () => {
    browser.localStorage.setItem(`project_top_menu_visible:${user.userId}`, "{oops");
    browser.localStorage.setItem(
        `project_top_menu_active_buttons:${user.userId}`,
        JSON.stringify([3])
    );
    await mountWithCleanup(WebClient);
    await openProject(1);
    expect(queryTexts()).toEqual(["Tasks"]);
});
