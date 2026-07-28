import tempfile
import unittest
from pathlib import Path

from scripts import context_budget


REPOSITORY_ROOT = Path(__file__).parents[2]


class ContextBudgetTest(unittest.TestCase):
    def test_current_routes_preserve_required_authorities(self):
        errors, _, report = context_budget.audit(
            REPOSITORY_ROOT,
            enforce_budget=False,
        )

        self.assertEqual([], errors)
        actual_skills = {
            path.name.removesuffix(".skill.md")
            for path in (REPOSITORY_ROOT / ".skills").glob("*.skill.md")
        }
        self.assertTrue(set(context_budget.REQUIRED_READS).issubset(actual_skills))
        self.assertTrue(report["largest_route_name"])

    def test_directory_and_glob_routes_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "docs").mkdir()

            directory_error = context_budget.route_path_error(root, "docs/")
            glob_error = context_budget.route_path_error(root, "docs/**/*.md")

            self.assertIn("directory", directory_error)
            self.assertIn("glob", glob_error)

    def test_missing_and_traversing_routes_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)

            missing_error = context_budget.route_path_error(root, ".ai/missing.md")
            traversal_error = context_budget.route_path_error(root, "../outside.md")

            self.assertIn("does not exist", missing_error)
            self.assertIn("traversal", traversal_error)

    def test_route_symlink_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            parent = Path(temporary_directory)
            root = parent / "repository"
            root.mkdir()
            outside = parent / "outside.md"
            outside.write_text("outside", encoding="utf-8")
            (root / "linked.md").symlink_to(outside)

            error = context_budget.route_path_error(root, "linked.md")

            self.assertIn("outside", error)

    def test_budget_overage_fails_only_when_enforced(self):
        actual = context_budget.Counts(bytes=101, words=51)
        limit = context_budget.Counts(bytes=100, words=50)

        strict_errors, strict_warnings = context_budget.budget_findings(
            "test",
            actual,
            limit,
            enforce=True,
        )
        report_errors, report_warnings = context_budget.budget_findings(
            "test",
            actual,
            limit,
            enforce=False,
        )

        self.assertEqual(1, len(strict_errors))
        self.assertEqual([], strict_warnings)
        self.assertEqual([], report_errors)
        self.assertEqual(1, len(report_warnings))


if __name__ == "__main__":
    unittest.main()
