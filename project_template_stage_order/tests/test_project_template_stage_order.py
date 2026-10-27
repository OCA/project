# Copyright 2026 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form
from odoo.tests.common import tagged

from .common import TestTemplateStageOrderCommon


@tagged("-at_install", "post_install")
class TestProjectTemplateStageOrder(TestTemplateStageOrderCommon):
    # -- Copy wizard -----------------------------------------------------

    def test_independent_copy_has_no_template_link(self):
        copy = self._copy_template("Test Independent Copy")
        self.assertFalse(copy.template_id)
        self.assertNotIn(copy, self.template.template_child_ids)

    def test_linked_copy_sets_template_id(self):
        copy = self._copy_template("Test Linked Copy", link_to_template=True)
        self.assertEqual(copy.template_id, self.template)
        self.assertIn(copy, self.template.template_child_ids)

    def test_linked_copy_flattens_to_root_template(self):
        child = self._copy_template("Test Child", link_to_template=True)
        grandchild_wizard = self.Wizard.create(
            {
                "template_id": child.id,
                "name": "Test Grandchild",
                "link_to_template": True,
            }
        )
        result = grandchild_wizard.action_confirm()
        grandchild = self.Project.browse(result["res_id"])
        self.assertEqual(grandchild.template_id, self.template)

    def test_source_is_template_stays_checked_after_copy(self):
        self._copy_template("Test Any Copy")
        self.assertTrue(self.template.is_template)

    def test_copy_never_copies_tasks(self):
        self.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": self.template.id,
                "stage_id": self.stage_new.id,
            }
        )
        copy = self._copy_template("Test No Tasks Copy")
        self.assertFalse(copy.task_ids)

    def test_copy_copies_custom_stage_order(self):
        self._sequence_for(self.template, self.stage_new).write({"sequence": 50})
        self._sequence_for(self.template, self.stage_done).write({"sequence": 10})
        copy = self._copy_template("Test Order Copy")
        self.assertEqual(self._sequence_for(copy, self.stage_new).sequence, 50)
        self.assertEqual(self._sequence_for(copy, self.stage_done).sequence, 10)

    # -- Blocking / propagation on linked copies --------------------------

    def test_linked_child_cannot_reorder_stages(self):
        linked = self._copy_template("Test Linked Child Reorder", link_to_template=True)
        row = self._sequence_for(linked, self.stage_new)
        with self.assertRaises(UserError):
            row.write({"sequence": 99})

    def test_template_reorder_propagates_to_linked_children_only(self):
        linked = self._copy_template(
            "Test Linked Child Propagate", link_to_template=True
        )
        independent = self._copy_template("Test Independent Child Propagate")
        self._sequence_for(self.template, self.stage_new).write({"sequence": 77})
        self.assertEqual(self._sequence_for(linked, self.stage_new).sequence, 77)
        self.assertNotEqual(
            self._sequence_for(independent, self.stage_new).sequence, 77
        )

    def test_linked_child_cannot_add_stage(self):
        linked = self._copy_template("Test Linked Child Add", link_to_template=True)
        with self.assertRaises(UserError):
            self.Stage.create(
                {
                    "name": "Test Extra Stage",
                    "project_ids": [(6, 0, [linked.id])],
                }
            )

    def test_linked_child_cannot_remove_stage(self):
        linked = self._copy_template("Test Linked Child Remove", link_to_template=True)
        with self.assertRaises(UserError):
            self.stage_new.with_context(default_project_id=linked.id).unlink()

    def test_template_add_stage_propagates_to_linked_children_only(self):
        linked = self._copy_template(
            "Test Linked Child New Stage", link_to_template=True
        )
        independent = self._copy_template("Test Independent Child New Stage")
        new_stage = self.Stage.create(
            {
                "name": "Test Propagated Stage",
                "project_ids": [(6, 0, [self.template.id])],
            }
        )
        self.assertIn(linked, new_stage.project_ids)
        self.assertNotIn(independent, new_stage.project_ids)

    def test_template_remove_stage_propagates_to_linked_children_only(self):
        other_project = self._create_project(name="Test Unrelated Project")
        self.stage_new.project_ids |= other_project
        linked = self._copy_template(
            "Test Linked Child Remove Propagate", link_to_template=True
        )
        self.stage_new.with_context(default_project_id=self.template.id).unlink()
        self.assertNotIn(linked, self.stage_new.project_ids)
        self.assertNotIn(self.template, self.stage_new.project_ids)
        self.assertIn(other_project, self.stage_new.project_ids)

    def test_unlink_template_blocked_when_children_exist(self):
        self._copy_template("Test Linked Child Delete Block", link_to_template=True)
        with self.assertRaises(UserError):
            self.template.unlink()

    def test_feature_disabled_allows_linked_child_to_change_stages(self):
        linked = self._copy_template(
            "Test Linked Child Disabled", link_to_template=True
        )
        self.env.company.task_stage_order_enabled = False
        row = self._sequence_for(linked, self.stage_new)
        row.write({"sequence": 99})
        self.assertEqual(row.sequence, 99)

    # -- Unlink button -----------------------------------------------------

    def test_unlink_from_template_clears_link(self):
        linked = self._copy_template("Test Unlink Target", link_to_template=True)
        linked.action_unlink_from_template()
        self.assertFalse(linked.template_id)
        self.assertNotIn(linked, self.template.template_child_ids)

    # -- Cannot turn a linked project into a template -----------------------

    def test_write_blocks_linked_project_as_template(self):
        linked = self._copy_template("Test Block Write Template", link_to_template=True)
        with self.assertRaises(ValidationError):
            linked.write({"is_template": True})

    def test_onchange_blocks_linked_project_as_template(self):
        linked = self._copy_template(
            "Test Block Onchange Template", link_to_template=True
        )
        with self.assertRaises(UserError):
            with Form(linked) as form:
                form.is_template = True

    def test_onchange_allows_marking_independent_project_as_template(self):
        partner = self.env["res.partner"].create({"name": "Test Onchange Partner"})
        other = self._create_project(
            name="Test Onchange Allows Template",
            is_template=True,
            user_id=self.env.user.id,
            partner_id=partner.id,
            alias_name="test-onchange-allows-template",
        )
        other.on_change_is_template()
        self.assertFalse(other.user_id)
        self.assertFalse(other.partner_id)
        self.assertFalse(other.alias_name)

    # -- Link to Another Project wizard -------------------------------------

    def test_link_wizard_blocks_different_stages(self):
        other = self._create_project(name="Test Other Stages Project")
        with self.assertRaises(UserError):
            self.LinkWizard.create(
                {"project_id": other.id, "template_id": self.template.id}
            ).action_check()

    def test_link_wizard_blocks_self_link(self):
        with self.assertRaises(UserError):
            self.LinkWizard.create(
                {"project_id": self.template.id, "template_id": self.template.id}
            ).action_check()

    def test_link_wizard_blocks_project_with_children(self):
        self._copy_template("Test Existing Child", link_to_template=True)
        other = self._create_project(name="Test Project As Source")
        with self.assertRaises(UserError):
            self.LinkWizard.create(
                {"project_id": self.template.id, "template_id": other.id}
            ).action_check()

    def test_link_wizard_confirm_links_and_applies_order(self):
        independent = self._copy_template("Test Independent For Link")
        self._sequence_for(self.template, self.stage_new).write({"sequence": 5})
        self._sequence_for(self.template, self.stage_done).write({"sequence": 1})
        wizard = self.LinkWizard.create(
            {"project_id": independent.id, "template_id": self.template.id}
        )
        wizard.action_check()
        self.assertEqual(wizard.state, "confirm")
        wizard.action_confirm()
        self.assertEqual(independent.template_id, self.template)
        self.assertEqual(self._sequence_for(independent, self.stage_new).sequence, 5)
        self.assertEqual(self._sequence_for(independent, self.stage_done).sequence, 1)

    def test_link_wizard_flattens_to_root_template(self):
        child = self._copy_template("Test Link Root Child", link_to_template=True)
        independent = self._copy_template("Test Link Root Independent")
        wizard = self.LinkWizard.create(
            {"project_id": independent.id, "template_id": child.id}
        )
        wizard.action_check()
        wizard.action_confirm()
        self.assertEqual(independent.template_id, self.template)

    def test_link_wizard_blocks_when_feature_disabled(self):
        other = self._create_project(
            name="Test Link Feature Disabled",
            type_ids=[(6, 0, [self.stage_new.id, self.stage_done.id])],
        )
        self.env.company.task_stage_order_enabled = False
        with self.assertRaises(UserError):
            self.LinkWizard.create(
                {"project_id": other.id, "template_id": self.template.id}
            ).action_check()
        self.env.company.task_stage_order_enabled = True

    def test_link_wizard_requires_template_selected(self):
        other = self._create_project(name="Test Link No Template Selected")
        with self.assertRaises(UserError):
            self.LinkWizard.create({"project_id": other.id}).action_check()

    # -- Action buttons (open the wizards) -----------------------------------

    def test_action_open_template_copy_wizard_returns_action(self):
        action = self.template.action_open_template_copy_wizard()
        self.assertEqual(action["res_model"], "project.template.copy.wizard")
        self.assertEqual(action["context"]["default_template_id"], self.template.id)

    def test_action_open_link_template_wizard_returns_action(self):
        action = self.template.action_open_link_template_wizard()
        self.assertEqual(action["res_model"], "project.link.template.wizard")
        self.assertEqual(action["context"]["default_project_id"], self.template.id)

    # -- _apply_stage_order_from guard ---------------------------------------

    def test_apply_stage_order_from_noop_when_disabled(self):
        self._sequence_for(self.template, self.stage_new).write({"sequence": 42})
        other = self._create_project(
            name="Test Apply Order Disabled",
            type_ids=[(6, 0, [self.stage_new.id, self.stage_done.id])],
        )
        self.env.company.task_stage_order_enabled = False
        other._apply_stage_order_from(self.template)
        self.env.company.task_stage_order_enabled = True
        self.assertNotEqual(self._sequence_for(other, self.stage_new).sequence, 42)

    def test_apply_stage_order_from_skips_stage_without_matching_target(self):
        self._sequence_for(self.template, self.stage_new).write({"sequence": 5})
        other = self._create_project(
            name="Test Apply Order Partial Stages",
            type_ids=[(6, 0, [self.stage_new.id])],
        )
        other._apply_stage_order_from(self.template)
        self.assertEqual(self._sequence_for(other, self.stage_new).sequence, 5)

    # -- write() on type_ids directly (project.project) ----------------------

    def test_write_type_ids_blocks_on_linked_project(self):
        linked = self._copy_template("Test Write Type Ids Block", link_to_template=True)
        with self.assertRaises(UserError):
            linked.write({"type_ids": [(4, self.stage_new.id)]})

    def test_write_type_ids_propagates_to_children(self):
        linked = self._copy_template(
            "Test Write Type Ids Propagate", link_to_template=True
        )
        extra_stage = self._create_stage(name="Test Write Propagate Stage")
        self.template.write({"type_ids": [(4, extra_stage.id)]})
        self.assertIn(linked, extra_stage.project_ids)

    def test_write_type_ids_on_independent_project_no_propagation(self):
        other = self._create_project(name="Test Write No Children")
        other.write({"type_ids": [(4, self.stage_new.id)]})
        self.assertIn(self.stage_new, other.type_ids)

    # -- unlink() happy path --------------------------------------------------

    def test_unlink_succeeds_without_children(self):
        other = self._create_project(name="Test Unlink No Children")
        other.unlink()
        self.assertFalse(other.exists())

    # -- write() project_ids on an existing stage (project.task.type) --------

    def test_write_project_ids_add_propagates_to_children(self):
        linked = self._copy_template(
            "Test Stage Write Add Propagate", link_to_template=True
        )
        extra_stage = self._create_stage(name="Test Stage Write Add")
        extra_stage.write({"project_ids": [(4, self.template.id)]})
        self.assertIn(linked, extra_stage.project_ids)

    def test_write_project_ids_remove_propagates_to_children(self):
        other_project = self._create_project(name="Test Stage Write Remove Other")
        self.stage_new.project_ids |= other_project
        linked = self._copy_template(
            "Test Stage Write Remove Propagate", link_to_template=True
        )
        self.stage_new.write({"project_ids": [(3, self.template.id)]})
        self.assertNotIn(linked, self.stage_new.project_ids)
        self.assertIn(other_project, self.stage_new.project_ids)

    def test_write_project_ids_blocks_direct_change_to_linked_project(self):
        linked = self._copy_template(
            "Test Stage Write Direct Linked Change", link_to_template=True
        )
        with self.assertRaises(UserError):
            self.stage_new.write({"project_ids": [(3, linked.id)]})
