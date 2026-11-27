/* Copyright 2026 OBS Solutions B.V.
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {ControlPanel} from "@web/search/control_panel/control_panel";
import {browser} from "@web/core/browser/browser";
import {onMounted} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {user} from "@web/core/user";

const PROJECT_MODEL = "project.project";
const VISIBLE_KEY = "project_top_menu_visible";
const BUTTONS_KEY = "project_top_menu_active_buttons";

/**
 * Odoo stores the top menu settings per user, per action and per record
 * (`<parent action>+<active_id>`), so every project starts with the top menu
 * hidden and with only its first button. This module keeps one choice per user
 * for all projects, in the browser's local storage, and applies it whenever a
 * project top menu is opened.
 */

function storageKey(key) {
    return `${key}:${user.userId}`;
}

function readStorage(key, fallback) {
    try {
        const value = browser.localStorage.getItem(storageKey(key));
        return value === null ? fallback : JSON.parse(value);
    } catch {
        return fallback;
    }
}

function writeStorage(key, value) {
    try {
        browser.localStorage.setItem(storageKey(key), JSON.stringify(value));
    } catch {
        // Storage can be full or disabled: the choice is then not kept.
    }
}

/**
 * @returns {Boolean} the top menu visibility chosen by the user, default true
 */
export function getTopMenuVisible() {
    return readStorage(VISIBLE_KEY, true) !== false;
}

/**
 * @returns {Object<string, boolean>} for each button (embedded action id),
 *      whether the user turned it on or off
 */
export function getTopMenuButtons() {
    const buttons = readStorage(BUTTONS_KEY, {});
    return buttons && typeof buttons === "object" && !Array.isArray(buttons)
        ? buttons
        : {};
}

patch(ControlPanel.prototype, {
    setup() {
        super.setup(...arguments);
        this.isProjectTopMenu =
            this.state.embeddedInfos.embeddedActions[0]?.parent_res_model ===
            PROJECT_MODEL;
        if (!this.isProjectTopMenu) {
            return;
        }
        // Odoo only stores the model of a setting when it creates it from the
        // top menu toggle; the field is required, so add it to every write.
        const handler = this.embeddedActionsConfigHandler;
        const setConfig = handler.setEmbeddedActionsConfig.bind(handler);
        handler.setEmbeddedActionsConfig = (config) =>
            setConfig({res_model: PROJECT_MODEL, ...config});

        const {embeddedInfos} = this.state;
        embeddedInfos.showEmbedded = getTopMenuVisible();
        embeddedInfos.visibleEmbeddedActions = this._projectTopMenuVisibleButtons();

        // With a single visible button Odoo opens the button dropdown each time
        // the top menu appears. That is meant for the moment the user turns the
        // top menu on, not for every project opened: skip it on opening.
        onMounted(() => {
            const root = this.root.el;
            if (!root || !embeddedInfos.showEmbedded) {
                return;
            }
            const skipAutoOpen = (ev) => {
                if (
                    !ev.isTrusted &&
                    ev.target.closest?.("[name='openEmbeddedActions']")
                ) {
                    ev.stopPropagation();
                }
            };
            root.addEventListener("click", skipAutoOpen, true);
            browser.setTimeout(
                () => root.removeEventListener("click", skipAutoOpen, true),
                500
            );
        });
    },

    /**
     * The buttons of this project to show. A button the user turned on or off
     * follows that choice; any other button is shown when Odoo shows it or
     * when it is the current one. A stored button the project does not have is
     * ignored. When no button is left, the current one is shown.
     *
     * @returns {Array<number|false>}
     */
    _projectTopMenuVisibleButtons() {
        const {embeddedActions, visibleEmbeddedActions, currentEmbeddedAction} =
            this.state.embeddedInfos;
        const currentId = currentEmbeddedAction?.id || false;
        const choices = getTopMenuButtons();
        const visible = embeddedActions
            .map((action) => action.id)
            .filter((id) =>
                String(id) in choices
                    ? choices[String(id)]
                    : visibleEmbeddedActions.includes(id) || id === currentId
            );
        if (!visible.length && embeddedActions.length) {
            visible.push(currentId);
        }
        return visible;
    },

    async onClickShowEmbedded() {
        if (!this.isProjectTopMenu) {
            return super.onClickShowEmbedded(...arguments);
        }
        const {embeddedInfos} = this.state;
        const show = !embeddedInfos.showEmbedded;
        writeStorage(VISIBLE_KEY, show);
        this.embeddedActionsConfigHandler.setEmbeddedActionsConfig({
            embedded_visibility: show,
            embedded_actions_visibility: embeddedInfos.visibleEmbeddedActions,
        });
        embeddedInfos.showEmbedded = show;
    },

    _setVisibility(actionId) {
        super._setVisibility(...arguments);
        if (!this.isProjectTopMenu) {
            return;
        }
        const choices = getTopMenuButtons();
        choices[String(actionId)] =
            this.state.embeddedInfos.visibleEmbeddedActions.includes(actionId);
        writeStorage(BUTTONS_KEY, choices);
    },
});
