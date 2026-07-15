import importlib.util
import json
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "github_governance.py"
SPEC = importlib.util.spec_from_file_location("github_governance_discovery", MODULE_PATH)
governance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(governance)


class Completed:
    def __init__(self, returncode=0, payload=None):
        self.returncode, self.stdout = returncode, json.dumps(payload) if payload is not None else ""
        self.stderr = "redacted API failure"


class FakeRunner:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        endpoint = command[-1]
        return self.responses.get(endpoint, Completed(returncode=1))


def repository_payload(security=True):
    payload = {"full_name": "acme/demo", "default_branch": "main", "delete_branch_on_merge": True}
    if security:
        payload["security_and_analysis"] = {
            "secret_scanning": {"status": "enabled"},
            "secret_scanning_push_protection": {"status": "enabled"},
            "dependabot_security_updates": {"status": "disabled"},
        }
    return payload


class GitHubDiscoveryTest(unittest.TestCase):
    def test_discovery_is_get_only_and_redacts_bypass_actor_details(self):
        rules = [
            {
                "type": "pull_request",
                "ruleset_id": 7,
                "ruleset_source_type": "Repository",
                "ruleset_source": "acme/demo",
                "parameters": {"required_approving_review_count": 1},
            },
        ]
        runner = FakeRunner(
            {
                "repos/acme/demo": Completed(payload=repository_payload()),
                "repos/acme/demo/branches/main": Completed(payload={"name": "main", "protected": True}),
                "repos/acme/demo/rules/branches/main?per_page=100": Completed(payload=[rules]),
                "repos/acme/demo/rulesets/7": Completed(
                    payload={"id": 7, "name": "main governance", "bypass_actors": [{"actor_id": 123}]}
                ),
                "repos/acme/demo/branches/main/protection": Completed(
                    payload={
                        "enforce_admins": {"enabled": True},
                        "required_status_checks": {"strict": True, "contexts": ["lint"]},
                        "required_pull_request_reviews": {
                            "required_approving_review_count": 0,
                            "require_last_push_approval": False,
                        },
                        "allow_force_pushes": {"enabled": False},
                    }
                ),
            }
        )

        result = governance.discover_github("acme/demo", "main", runner=runner)

        self.assertEqual(result["rulesets"][0]["has_bypass_actors"], True)
        self.assertEqual(result["legacy_branch_protection"]["status"], "configured")
        self.assertNotIn("123", json.dumps(result))
        for command, kwargs in runner.calls:
            self.assertEqual(command[command.index("--method") + 1], "GET")
            self.assertIn("X-GitHub-Api-Version: 2026-03-10", command)
            self.assertEqual(kwargs["timeout"], 30)
            self.assertFalse({"POST", "PUT", "PATCH", "DELETE"} & set(command))

    def test_admin_invisible_fields_are_unknown(self):
        rules = [
            {
                "type": "pull_request",
                "ruleset_id": 9,
                "ruleset_source_type": "Repository",
                "ruleset_source": [],
            }
        ]
        runner = FakeRunner(
            {
                "repos/acme/demo": Completed(payload=repository_payload(security=False)),
                "repos/acme/demo/branches/main": Completed(payload={"name": "main", "protected": True}),
                "repos/acme/demo/rules/branches/main?per_page=100": Completed(payload=[rules]),
            }
        )

        result = governance.discover_github("acme/demo", "main", runner=runner)

        self.assertEqual(result["security"]["secret_scanning"], "unknown")
        self.assertEqual(result["rulesets"][0]["has_bypass_actors"], "unknown")
        self.assertEqual(result["legacy_branch_protection"]["status"], "unknown")
        self.assertEqual(result["effective_rules"][0]["source"], "unknown")

    def test_unprotected_branch_skips_legacy_admin_endpoint(self):
        runner = FakeRunner(
            {
                "repos/acme/demo": Completed(payload=repository_payload()),
                "repos/acme/demo/branches/main": Completed(payload={"name": "main", "protected": False}),
                "repos/acme/demo/rules/branches/main?per_page=100": Completed(payload=[[]]),
            }
        )

        result = governance.discover_github("acme/demo", "main", runner=runner)

        self.assertEqual(result["legacy_branch_protection"]["status"], "absent")
        endpoints = [command[-1] for command, _ in runner.calls]
        self.assertNotIn("repos/acme/demo/branches/main/protection", endpoints)

    def test_required_read_failure_stops_closed(self):
        runner = FakeRunner({"repos/acme/demo": Completed(returncode=1)})

        with self.assertRaises(governance.PolicyError):
            governance.discover_github("acme/demo", "main", runner=runner)

    def test_runner_failure_stops_closed(self):
        def unavailable(*args, **kwargs):
            raise OSError("gh unavailable")

        with self.assertRaises(governance.PolicyError):
            governance.discover_github("acme/demo", "main", runner=unavailable)

    def test_invalid_repository_target_is_rejected_before_api_call(self):
        runner = FakeRunner({})

        with self.assertRaises(governance.PolicyError):
            governance.discover_github("../..", "main", runner=runner)

        self.assertEqual(runner.calls, [])


if __name__ == "__main__":
    unittest.main()
