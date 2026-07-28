import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

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

    def test_baseline_wording_is_enforced_only_in_strict_mode(self):
        finding = "canonical baseline marker is missing"
        with mock.patch.object(
            context_budget,
            "baseline_contract_errors",
            return_value=[finding],
        ) as contract_check:
            non_strict_errors, _, _ = context_budget.audit(
                REPOSITORY_ROOT,
                enforce_budget=False,
            )

        contract_check.assert_not_called()
        self.assertNotIn(finding, non_strict_errors)

        with mock.patch.object(
            context_budget,
            "baseline_contract_errors",
            return_value=[finding],
        ) as contract_check:
            strict_errors, _, _ = context_budget.audit(
                REPOSITORY_ROOT,
                enforce_budget=True,
            )

        contract_check.assert_called_once_with(REPOSITORY_ROOT)
        self.assertIn(finding, strict_errors)

    def test_baseline_preserves_safety_contract_and_headroom(self):
        agents = (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        normalized_agents = " ".join(agents.split())
        for marker in (
            "CLAUDE.md",
            "completely and follow it before acting",
            "make format && make lint",
            ".ai/guardrails.md",
            ".skills/*.skill.md",
            "never store secrets",
        ):
            self.assertIn(marker, normalized_agents)

        manual = (REPOSITORY_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        normalized_manual = " ".join(manual.split())
        for marker in (
            "Binding vendor-neutral manual",
            "Every agent reads it completely at task start",
            "Authority: guardrails > security",
            "## 2. Start every task",
            "docs/development-handoff.md",
            "read every selected source completely",
            "one issue, one task branch, and a reviewed PR",
            "Architectural changes require an approved ADR first",
            "Use the pull-request template completely",
            ".ai/review-checklist.md",
            "no direct push to `main`",
            "make doctor",
            "## 13. Escalation",
            "## 14. Definition of done",
        ):
            self.assertIn(marker, normalized_manual)

        guardrails = (
            REPOSITORY_ROOT / ".ai/guardrails.md"
        ).read_text(encoding="utf-8")
        normalized_guardrails = " ".join(guardrails.split())
        for marker in (
            "Never write secrets into the repository",
            "Never push directly to main/master",
            "Never bypass hooks or checks",
            "Never lower the security level",
            "Never run destructive operations without explicit human approval",
            "Never fabricate results",
        ):
            self.assertIn(marker, normalized_guardrails)

        router = (REPOSITORY_ROOT / ".ai/README.md").read_text(encoding="utf-8")
        normalized_router = " ".join(router.split())
        for marker in (
            "Quality takes priority over context reduction",
            "Read every file selected by the baseline or task route completely",
            "Broaden discovery and reading until uncertainty is resolved",
            "Never use a context budget to skip a relevant source",
            "Reading protocol by task type",
        ):
            self.assertIn(marker, normalized_router)

        baseline = context_budget.Counts()
        for baseline_file in context_budget.BASELINE_FILES:
            baseline += context_budget.count_file(REPOSITORY_ROOT / baseline_file)
        budget_errors, budget_warnings = context_budget.budget_findings(
            "baseline",
            baseline,
            context_budget.Counts(
                context_budget.BASELINE_BYTE_LIMIT,
                context_budget.BASELINE_WORD_LIMIT,
            ),
            enforce=True,
        )

        self.assertEqual([], budget_errors)
        self.assertEqual([], budget_warnings)

    def test_requirements_route_preserves_method_template_and_headroom(self):
        skill_path = REPOSITORY_ROOT / ".skills/requirements.skill.md"
        skill = skill_path.read_text(encoding="utf-8")
        normalized_skill = " ".join(skill.split()).lower()
        for marker in (
            "one fork at a time",
            "recommended draft",
            "zero-based",
            "purpose or metric",
            "existing assets, constraints, and platform limits",
            "fr-00x/nfr-00x",
            "moscow",
            "what must hold and why",
            "open questions",
            "japanese",
            "claude.md §13",
        ):
            self.assertIn(marker, normalized_skill)

        template = (
            REPOSITORY_ROOT / "docs/foundation/templates/requirements.md"
        ).read_text(encoding="utf-8")
        for heading in (
            "## 1. Terms",
            "## 2. Assumptions and constraints",
            "## 3. Purpose and scope",
            "## 4. Functional requirements",
            "## 5. Non-functional requirements",
            "## 6. Data requirements",
            "## 7. External interfaces and dependencies",
            "## 8. Infrastructure and cost estimate",
            "## 9. Operational requirements",
            "## 10. Acceptance criteria",
            "## 11. Risks",
            "## 12. Milestones",
            "## 13. Open questions",
        ):
            self.assertIn(heading, template)
        for field in (
            "ISO/IEC 25010",
            "Measurement method",
            "Cost assumptions",
            "unit prices as of",
            "Fixed / month",
            "Usage-based basis",
            "Increment per",
            "Verifies (req IDs)",
            "Likelihood",
            "Target date",
            "Blocks (req IDs)",
        ):
            self.assertIn(field, template)

        baseline = context_budget.Counts()
        for baseline_file in context_budget.BASELINE_FILES:
            baseline += context_budget.count_file(REPOSITORY_ROOT / baseline_file)
        route_errors, route = context_budget.measure_skill_route(
            REPOSITORY_ROOT,
            "requirements",
            skill_path,
            baseline,
        )
        budget_errors, budget_warnings = context_budget.budget_findings(
            "requirements",
            route,
            context_budget.Counts(
                context_budget.ROUTE_BYTE_LIMIT,
                context_budget.ROUTE_WORD_LIMIT,
            ),
            enforce=True,
        )

        self.assertEqual([], route_errors)
        self.assertEqual([], budget_errors)
        self.assertEqual([], budget_warnings)

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
