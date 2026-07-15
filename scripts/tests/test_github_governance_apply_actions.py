import importlib.util
import unittest
from pathlib import Path

from test_github_governance_comparison import CHECKS, resolved_policy, ruleset_inventory


ROOT = Path(__file__).parents[2]
MODULE_PATH = ROOT / "scripts/github_governance.py"
SPEC = importlib.util.spec_from_file_location("github_governance_apply_actions", MODULE_PATH)
governance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(governance)

REPOSITORY = "acme/demo"


def inventory():
    result = ruleset_inventory()
    result["branch"]["protected"] = False
    result["effective_rules"] = []
    result["rulesets"] = []
    return result


class ApplyActionPlanningTest(unittest.TestCase):
    def test_missing_ruleset_creates_owned_ruleset_action(self):
        result = governance.build_apply_actions(resolved_policy(), inventory())
        self.assertEqual(result["status"], "ready")
        self.assertEqual(
            [action["id"] for action in result["actions"]],
            ["branch.ruleset"],
        )
        action = result["actions"][0]
        self.assertEqual(action["method"], "POST")
        self.assertEqual(action["endpoint"], f"repos/{REPOSITORY}/rulesets")
        self.assertEqual(action["body"]["name"], governance.MANAGED_RULESET_NAME)
        self.assertEqual(
            action["body"]["conditions"]["ref_name"]["include"],
            ["refs/heads/main"],
        )
        pull = action["body"]["rules"][0]["parameters"]
        self.assertEqual(pull["required_approving_review_count"], 0)
        self.assertTrue(pull["required_review_thread_resolution"])
        checks = action["body"]["rules"][1]["parameters"]
        self.assertEqual(
            checks["required_status_checks"],
            [{"context": check} for check in CHECKS],
        )
        self.assertTrue(checks["strict_required_status_checks_policy"])

    def test_drifted_existing_repository_ruleset_update_is_rejected(self):
        current = ruleset_inventory()
        current["effective_rules"] = []
        with self.assertRaises(governance.PolicyError):
            governance.build_apply_actions(resolved_policy(), current)

    def test_common_actions_are_ordered_and_describe_side_effects(self):
        current = ruleset_inventory()
        current["repository"]["delete_branch_on_merge"] = False
        current["security"] = {
            "dependabot_security_updates": "enabled",
            "push_protection": "disabled",
            "secret_scanning": "disabled",
        }
        result = governance.build_apply_actions(resolved_policy(), current)
        self.assertEqual(
            [action["id"] for action in result["actions"]],
            [
                "security.secret_scanning",
                "repository.delete_branch_on_merge",
                "security.dependabot_security_updates",
            ],
        )
        self.assertEqual(result["actions"][0]["method"], "PATCH")
        self.assertIn(
            "pushes_containing_detected_secrets_are_rejected",
            result["actions"][0]["side_effects"],
        )
        self.assertEqual(result["actions"][2]["method"], "DELETE")
        self.assertIn(
            "dependabot_security_updates_are_disabled",
            result["actions"][2]["side_effects"],
        )

    def test_compliant_inventory_has_no_actions(self):
        result = governance.build_apply_actions(
            resolved_policy(),
            ruleset_inventory(),
        )
        self.assertEqual(result["status"], "compliant")
        self.assertEqual(result["actions"], [])

    def test_unknown_or_unobserved_preflight_blocks_all_actions(self):
        unknown = ruleset_inventory()
        unknown["rulesets"][0]["has_bypass_actors"] = "unknown"
        unobserved = inventory()
        unobserved["observed_checks"] = ["lint"]
        for current in (unknown, unobserved):
            with self.subTest(current=current), self.assertRaises(governance.PolicyError):
                governance.build_apply_actions(resolved_policy(), current)

    def test_drifted_legacy_backend_is_rejected(self):
        with self.assertRaises(governance.PolicyError):
            governance.build_apply_actions(resolved_policy("legacy_branch_protection"), inventory())

    def test_organization_ruleset_with_managed_name_is_not_updated(self):
        current = ruleset_inventory()
        current["rulesets"][0]["source"] = "acme"
        current["rulesets"][0]["source_type"] = "Organization"
        for rule in current["effective_rules"]:
            rule["source"] = "acme"
            rule["source_type"] = "Organization"
        result = governance.build_apply_actions(resolved_policy(), current)
        self.assertEqual(result["actions"][0]["method"], "POST")
        self.assertEqual(result["actions"][0]["endpoint"], f"repos/{REPOSITORY}/rulesets")

    def test_repository_ownership_matching_is_case_insensitive(self):
        current = ruleset_inventory()
        current["rulesets"][0]["source"] = "Acme/Demo"
        current["effective_rules"] = []
        with self.assertRaises(governance.PolicyError):
            governance.build_apply_actions(resolved_policy(), current)


if __name__ == "__main__":
    unittest.main()
