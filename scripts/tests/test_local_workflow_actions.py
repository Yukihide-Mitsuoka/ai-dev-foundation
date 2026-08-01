import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).parents[2]


class LocalWorkflowActionsTest(unittest.TestCase):
    CASES = {
        "container": {
            "workflow": ".github/workflows/container.yml",
            "action": "scripts/actions/container-scan/action.yml",
            "implementation": "docker build",
            "pinned_action": (
                "aquasecurity/trivy-action@"
                "ed142fd0673e97e23eac54620cfb913e5ce36c25"
            ),
        },
        "dast": {
            "workflow": ".github/workflows/dast.yml",
            "action": "scripts/actions/dast-baseline/action.yml",
            "implementation": "zaproxy/action-baseline@",
            "pinned_action": (
                "zaproxy/action-baseline@"
                "de8ad967d3548d44ef623df22cf95c3b0baf8b25"
            ),
        },
        "labels": {
            "workflow": ".github/workflows/labels-sync.yml",
            "action": "scripts/actions/labels-sync/action.yml",
            "implementation": "crazy-max/ghaction-github-labeler@",
            "pinned_action": (
                "crazy-max/ghaction-github-labeler@"
                "24d110aa46a59976b8a7f35518cb7f14f434c916"
            ),
        },
    }

    def test_protected_callers_keep_boundaries_and_delegate_implementation(self):
        for name, case in self.CASES.items():
            with self.subTest(name=name):
                workflow = (REPOSITORY_ROOT / case["workflow"]).read_text(
                    encoding="utf-8"
                )
                self.assertIn("permissions:", workflow)
                self.assertIn("actions/checkout@", workflow)
                self.assertIn(f"uses: ./{case['action'].removesuffix('/action.yml')}", workflow)
                self.assertNotIn(case["implementation"], workflow)
                self.assertNotIn("uses: Yukihide-Mitsuoka/ai-dev-foundation/", workflow)

    def test_synchronized_local_actions_hold_pinned_implementations(self):
        for name, case in self.CASES.items():
            with self.subTest(name=name):
                action_path = REPOSITORY_ROOT / case["action"]
                self.assertTrue(action_path.is_file())
                action = action_path.read_text(encoding="utf-8")
                self.assertIn("using: composite", action)
                self.assertIn(case["pinned_action"], action)

    def test_container_caller_runs_when_local_implementation_changes(self):
        workflow = (
            REPOSITORY_ROOT / ".github" / "workflows" / "container.yml"
        ).read_text(encoding="utf-8")

        self.assertIn('"scripts/actions/container-scan/**"', workflow)


if __name__ == "__main__":
    unittest.main()
