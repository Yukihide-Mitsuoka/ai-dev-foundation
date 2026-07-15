import copy
import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "github_governance.py"
SPEC = importlib.util.spec_from_file_location("github_governance", MODULE_PATH)
governance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(governance)

KNOWN_RULES = {"GR-010", "GR-011", "GR-012", "SEC-002", "SEC-003"}


def foundation_policy():
    return {
        "schema_version": 1,
        "managed_by": "ai-dev-foundation",
        "minimums": {
            "pull_request_required": {"value": True, "rule_refs": ["GR-010"]},
            "status_checks_required": {"value": True, "rule_refs": ["GR-012"]},
            "force_pushes_allowed": {"value": False, "rule_refs": ["GR-011"]},
            "admin_bypass_allowed": {"value": False, "rule_refs": ["GR-010", "GR-012"]},
            "secret_scanning_enabled": {"value": True, "rule_refs": ["SEC-002"]},
            "push_protection_enabled": {"value": True, "rule_refs": ["SEC-002"]},
            "vulnerability_alerts_enabled": {"value": True, "rule_refs": ["SEC-003"]},
            "private_vulnerability_reporting_enabled": {
                "value": True,
                "rule_refs": ["SEC-003"],
            },
        },
        "defaults": {
            "target_branch": "main",
            "enforcement_backend": "ruleset",
            "required_approvals": 0,
            "require_last_push_approval": False,
            "required_checks": ["lint", "test"],
            "dependency_update_provider": "renovate",
            "delete_branch_on_merge": False,
        },
    }


class GovernancePolicyTest(unittest.TestCase):
    def resolve(self, foundation=None, repository=None):
        return governance.resolve_policy(
            foundation or foundation_policy(),
            repository or {"schema_version": 1, "overrides": {}},
            KNOWN_RULES,
        )

    def assert_policy_error(self, foundation=None, repository=None):
        with self.assertRaises(governance.PolicyError):
            self.resolve(foundation, repository)

    def test_repository_overrides_only_operational_defaults(self):
        result = self.resolve(
            repository={
                "schema_version": 1,
                "overrides": {
                    "required_approvals": 1,
                    "require_last_push_approval": True,
                    "required_checks": ["doctor", "secret-scan"],
                    "dependency_update_provider": "dependabot",
                },
            }
        )

        self.assertEqual(result["settings"]["required_approvals"], 1)
        self.assertEqual(result["settings"]["required_checks"], ["doctor", "secret-scan"])
        self.assertTrue(result["minimums"]["pull_request_required"]["value"])

    def test_unknown_fields_and_minimum_overrides_are_rejected(self):
        for repository in (
            {"schema_version": 1, "overrides": {}, "extra": True},
            {"schema_version": 1, "overrides": {"pull_request_required": False}},
        ):
            with self.subTest(repository=repository):
                self.assert_policy_error(repository=repository)

    def test_invalid_operational_values_are_rejected(self):
        invalid_overrides = (
            {"target_branch": "feature//main"},
            {"target_branch": "release/.hidden"},
            {"required_approvals": -1},
            {"enforcement_backend": "automatic"},
            {"enforcement_backend": ["ruleset"]},
            {"required_checks": []},
            {"required_checks": ["lint", "lint"]},
            {"required_checks": ["lint\ntest"]},
            {"required_checks": ["lint", ["test"]]},
            {"dependency_update_provider": ["renovate", "dependabot"]},
            {"required_approvals": 0, "require_last_push_approval": True},
        )
        for overrides in invalid_overrides:
            with self.subTest(overrides=overrides):
                self.assert_policy_error(repository={"schema_version": 1, "overrides": overrides})

    def test_foundation_minimum_values_and_rule_refs_are_strict(self):
        for mutate in (
            lambda policy: policy["minimums"]["force_pushes_allowed"].update(value=True),
            lambda policy: policy["minimums"]["pull_request_required"].update(rule_refs=[]),
            lambda policy: policy["minimums"]["pull_request_required"].update(rule_refs=[["GR-010"]]),
            lambda policy: policy["minimums"]["pull_request_required"].update(rule_refs=["GR-011"]),
            lambda policy: policy["minimums"]["pull_request_required"].update(rule_refs=["GR-999"]),
        ):
            policy = copy.deepcopy(foundation_policy())
            mutate(policy)
            with self.subTest(policy=policy):
                self.assert_policy_error(foundation=policy)

    def test_schema_version_and_manager_are_fixed(self):
        for key, value in (("schema_version", 2), ("managed_by", "downstream")):
            policy = foundation_policy()
            policy[key] = value
            with self.subTest(key=key):
                self.assert_policy_error(foundation=policy)


if __name__ == "__main__":
    unittest.main()
