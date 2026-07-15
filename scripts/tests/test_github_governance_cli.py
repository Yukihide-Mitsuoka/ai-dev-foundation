import contextlib
import importlib.util
import io
import json
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).parents[2]
MODULE_PATH = ROOT / "scripts/github_governance.py"
SPEC = importlib.util.spec_from_file_location("github_governance_cli", MODULE_PATH)
governance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(governance)


class GovernanceCliTest(unittest.TestCase):
    def run_cli(self, command, status="compliant"):
        report = {"repository": "acme/demo", "status": status}
        stdout = io.StringIO()
        with (
            mock.patch.object(
                governance,
                "discover_github",
                return_value={"inventory": True},
            ) as discover,
            mock.patch.object(governance, "compare_governance", return_value=report),
            contextlib.redirect_stdout(stdout),
        ):
            exit_code = governance.main([command, "--root", str(ROOT), "--repo", "acme/demo"])
        return exit_code, json.loads(stdout.getvalue()), discover

    def test_plan_reports_drift_without_failing(self):
        exit_code, report, discover = self.run_cli("plan", "drift")

        self.assertEqual(exit_code, 0)
        self.assertEqual(report["status"], "drift")
        discover.assert_called_once_with("acme/demo", "main")

    def test_audit_exit_code_distinguishes_compliance_from_incomplete_audit(self):
        for status, expected in (("compliant", 0), ("drift", 1), ("unknown", 1)):
            with self.subTest(status=status):
                exit_code, report, _ = self.run_cli("audit", status)
                self.assertEqual(exit_code, expected)
                self.assertEqual(report["status"], status)

    def test_github_read_failure_returns_policy_error_exit(self):
        stderr = io.StringIO()
        with (
            mock.patch.object(
                governance,
                "discover_github",
                side_effect=governance.PolicyError("read failed"),
            ),
            contextlib.redirect_stderr(stderr),
        ):
            exit_code = governance.main(
                ["audit", "--root", str(ROOT), "--repo", "acme/demo"]
            )

        self.assertEqual(exit_code, 2)
        self.assertIn("governance policy error: read failed", stderr.getvalue())

    def test_online_commands_require_explicit_repository(self):
        for command in ("plan", "audit"):
            with self.subTest(command=command), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    governance.main([command, "--root", str(ROOT)])
                self.assertEqual(raised.exception.code, 2)

    def test_validate_remains_offline(self):
        stdout = io.StringIO()
        with (
            mock.patch.object(governance, "discover_github") as discover,
            contextlib.redirect_stdout(stdout),
        ):
            exit_code = governance.main(["validate", "--root", str(ROOT)])

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["managed_by"], "ai-dev-foundation")
        discover.assert_not_called()


if __name__ == "__main__":
    unittest.main()
