import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]
MODULE_PATH = ROOT / "scripts/github_governance.py"
SPEC = importlib.util.spec_from_file_location("github_governance_comparison", MODULE_PATH)
governance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(governance)

CHECKS = sorted(["lint", "test", "build", "doctor", "link-check", "pr-quality", "secret-scan", "dependency-scan", "license-check"])


def resolved_policy(backend="ruleset"):
    return {
        "minimums": {
            "pull_request_required": {"rule_refs": ["GR-010"]},
            "status_checks_required": {"rule_refs": ["GR-012"]},
            "force_pushes_allowed": {"rule_refs": ["GR-011"]},
            "admin_bypass_allowed": {"rule_refs": ["GR-010", "GR-012"]},
            "secret_scanning_enabled": {"rule_refs": ["SEC-002"]},
            "push_protection_enabled": {"rule_refs": ["SEC-002"]},
        },
        "settings": {
            "target_branch": "main",
            "enforcement_backend": backend,
            "required_approvals": 0,
            "require_last_push_approval": False,
            "required_checks": CHECKS,
            "dependency_update_provider": "renovate",
            "delete_branch_on_merge": True,
        },
    }


def ruleset_inventory():
    rule_base = {"ruleset_id": 7, "source": "acme/demo", "source_type": "Repository"}
    return {
        "branch": {"name": "main", "protected": True},
        "effective_rules": [
            {
                **rule_base,
                "type": "pull_request",
                "parameters": {"required_approving_review_count": 0, "require_last_push_approval": False},
            },
            {**rule_base, "type": "required_status_checks", "parameters": {"contexts": CHECKS}},
            {**rule_base, "type": "non_fast_forward", "parameters": {}},
        ],
        "legacy_branch_protection": {"status": "absent"},
        "observed_checks": CHECKS,
        "repository": {"delete_branch_on_merge": True, "full_name": "acme/demo"},
        "rulesets": [
            {
                "has_bypass_actors": False,
                "id": 7,
                "name": "ai-dev-foundation: branch-governance",
                "source": "acme/demo",
                "source_type": "Repository",
            }
        ],
        "security": {"dependabot_security_updates": "disabled", "push_protection": "enabled", "secret_scanning": "enabled"},
    }


def legacy_inventory():
    inventory = ruleset_inventory()
    inventory["effective_rules"] = []
    inventory["rulesets"] = []
    inventory["legacy_branch_protection"] = {
        "allow_force_pushes": False,
        "enforce_admins": True,
        "required_pull_request_reviews": {"require_last_push_approval": False, "required_approvals": 0},
        "required_status_checks": {"contexts": CHECKS, "strict": True},
        "status": "configured",
    }
    return inventory


def control(report, control_id):
    return next(item for item in report["controls"] if item["id"] == control_id)


class GovernanceComparisonTest(unittest.TestCase):
    def test_ruleset_report_is_compliant_and_deterministic(self):
        first = governance.compare_governance(resolved_policy(), ruleset_inventory())
        second = governance.compare_governance(resolved_policy(), ruleset_inventory())

        self.assertEqual(first["status"], "compliant")
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        self.assertEqual([item["id"] for item in first["controls"]], sorted(item["id"] for item in first["controls"]))
        self.assertEqual(first["unmanaged"]["effective_rules"], [])
        self.assertIsNone(first["unmanaged"]["legacy_branch_protection"])

    def test_drift_and_unmanaged_controls_are_reported(self):
        inventory = ruleset_inventory()
        status_rule = next(rule for rule in inventory["effective_rules"] if rule["type"] == "required_status_checks")
        status_rule["parameters"]["contexts"] = ["lint"]
        inventory["legacy_branch_protection"] = {"status": "configured"}
        inventory["effective_rules"].append(
            {"parameters": {}, "ruleset_id": 8, "source": "acme/demo", "source_type": "Repository", "type": "required_linear_history"}
        )

        report = governance.compare_governance(resolved_policy(), inventory)

        self.assertEqual(report["status"], "drift")
        self.assertEqual(control(report, "branch.required_status_checks")["status"], "drift")
        self.assertEqual(len(report["unmanaged"]["effective_rules"]), 1)
        self.assertEqual(report["unmanaged"]["legacy_branch_protection"]["status"], "configured")

    def test_admin_invisible_control_makes_report_unknown(self):
        inventory = ruleset_inventory()
        inventory["rulesets"][0]["has_bypass_actors"] = "unknown"

        report = governance.compare_governance(resolved_policy(), inventory)

        self.assertEqual(report["status"], "unknown")
        self.assertEqual(control(report, "branch.admin_bypass_allowed")["status"], "unknown")

    def test_unobserved_required_check_is_drift(self):
        inventory = ruleset_inventory()
        inventory["observed_checks"] = CHECKS[:-1]

        report = governance.compare_governance(resolved_policy(), inventory)

        observed = control(report, "branch.required_status_checks_observed")
        self.assertEqual(observed["status"], "drift")
        self.assertEqual(observed["current"], CHECKS[:-1])

    def test_legacy_backend_can_be_compliant(self):
        report = governance.compare_governance(resolved_policy("legacy_branch_protection"), legacy_inventory())

        self.assertEqual(report["status"], "compliant")
        self.assertEqual(control(report, "branch.enforcement_backend")["current"], "legacy_branch_protection")

    def test_duplicate_managed_rulesets_are_rejected(self):
        inventory = ruleset_inventory()
        duplicate = copy.deepcopy(inventory["rulesets"][0])
        duplicate["id"] = 9
        inventory["rulesets"].append(duplicate)

        with self.assertRaises(governance.PolicyError):
            governance.compare_governance(resolved_policy(), inventory)


if __name__ == "__main__":
    unittest.main()
