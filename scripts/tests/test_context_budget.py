import tempfile
import unittest
from datetime import date
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

    def test_budget_soft_limit_warns_without_failing(self):
        actual = context_budget.Counts(bytes=90, words=89)
        limit = context_budget.Counts(bytes=100, words=100)

        errors, warnings = context_budget.budget_findings(
            "test",
            actual,
            limit,
            enforce=True,
        )

        self.assertEqual([], errors)
        self.assertEqual(1, len(warnings))
        self.assertIn("90%", warnings[0])
        self.assertIn("90/100 bytes", warnings[0])

    def test_adr_index_rejects_missing_duplicate_and_mismatched_entries(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            directory = root / "docs/foundation/adr"
            directory.mkdir(parents=True)
            (directory / "0001-first.md").write_text(
                "---\nstatus: accepted\nupdated: 2026-07-01\n---\n",
                encoding="utf-8",
            )
            (directory / "0002-second.md").write_text(
                "---\nstatus: proposed\nupdated: 2026-07-02\n---\n",
                encoding="utf-8",
            )
            (directory / "README.md").write_text(
                "| # | Title | Scope | Status | Date |\n"
                "|---|-------|-------|--------|------|\n"
                "| [0001](0001-first.md) | First | context | rejected | 2026-07-01 |\n"
                "| [0001](0001-first.md) | First | context | rejected | 2026-07-01 |\n"
                "| [0003](0003-gone.md) | Gone | context | accepted | 2026-07-03 |\n",
                encoding="utf-8",
            )

            errors = context_budget.validate_adr_index(root)

            self.assertTrue(any("duplicate target: 0001-first.md" in error for error in errors))
            self.assertTrue(any("duplicate number: 0001" in error for error in errors))
            self.assertTrue(any("missing entry: 0002-second.md" in error for error in errors))
            self.assertTrue(any("stale entry: 0003-gone.md" in error for error in errors))
            self.assertTrue(any("status 'rejected'" in error for error in errors))

    def test_adr_index_supports_legacy_table_metadata(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            directory = root / "docs/foundation/adr"
            directory.mkdir(parents=True)
            (directory / "0001-legacy.md").write_text(
                "# ADR-0001: Legacy\n\n"
                "| Field | Value |\n"
                "|-------|-------|\n"
                "| Status | accepted |\n"
                "| Date | 2026-07-01 |\n",
                encoding="utf-8",
            )
            (directory / "README.md").write_text(
                "| # | Title | Scope | Status | Date |\n"
                "|---|-------|-------|--------|------|\n"
                "| [0001](0001-legacy.md) | Legacy | context | accepted | 2026-07-01 |\n",
                encoding="utf-8",
            )

            errors = context_budget.validate_adr_index(root)

            self.assertEqual([], errors)

    def test_guide_index_rejects_missing_duplicate_and_stale_entries(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            directory = root / "docs/foundation/guides"
            directory.mkdir(parents=True)
            (directory / "current.md").write_text("# Current\n", encoding="utf-8")
            (directory / "missing.md").write_text("# Missing\n", encoding="utf-8")
            (directory / "README.md").write_text(
                "| Guide | Purpose |\n"
                "|-------|---------|\n"
                "| [current.md](current.md) | Current |\n"
                "| [current.md](current.md) | Current again |\n"
                "| [gone.md](gone.md) | Gone |\n",
                encoding="utf-8",
            )

            errors = context_budget.validate_guide_index(root)

            self.assertTrue(any("duplicate target: current.md" in error for error in errors))
            self.assertTrue(any("missing entry: missing.md" in error for error in errors))
            self.assertTrue(any("stale entry: gone.md" in error for error in errors))

    def test_handoff_warnings_cover_size_and_freshness_without_errors(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            handoff = root / "docs/development-handoff.md"
            handoff.parent.mkdir()
            handoff.write_text(
                "---\nupdated: 2026-01-01\n---\n"
                + "word " * (context_budget.HANDOFF_WORD_WARNING + 1),
                encoding="utf-8",
            )

            warnings = context_budget.handoff_warnings(
                root,
                current_date=date(2026, 2, 15),
            )

            self.assertEqual(2, len(warnings))
            self.assertTrue(any("unusually large" in warning for warning in warnings))
            self.assertTrue(any("may be stale" in warning for warning in warnings))

    def test_handoff_warning_rejects_invalid_or_future_updated_date(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            handoff = root / "docs/development-handoff.md"
            handoff.parent.mkdir()
            handoff.write_text("---\nupdated: unknown\n---\n", encoding="utf-8")

            invalid_warnings = context_budget.handoff_warnings(
                root,
                current_date=date(2026, 2, 15),
            )
            handoff.write_text("---\nupdated: 2026-02-16\n---\n", encoding="utf-8")
            future_warnings = context_budget.handoff_warnings(
                root,
                current_date=date(2026, 2, 15),
            )

            self.assertEqual(1, len(invalid_warnings))
            self.assertIn("invalid ISO updated date", invalid_warnings[0])
            self.assertEqual(1, len(future_warnings))
            self.assertIn("future", future_warnings[0])


if __name__ == "__main__":
    unittest.main()
