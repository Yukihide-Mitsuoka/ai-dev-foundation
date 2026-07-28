#!/usr/bin/env python3
"""Validate declared AI context routes and model-independent size budgets."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


BASELINE_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    ".ai/README.md",
    ".ai/guardrails.md",
)
BASELINE_BYTE_LIMIT = 18_500
BASELINE_WORD_LIMIT = 2_600
ROUTE_BYTE_LIMIT = 46_000
ROUTE_WORD_LIMIT = 6_500
READS_PATTERN = re.compile(r"^reads:\s*\[(.*)]\s*$", re.MULTILINE)
GLOB_CHARACTERS = frozenset("*?[")
REQUIRED_READS = {
    "architecture": {".ai/architecture.md", "docs/foundation/adr/README.md"},
    "bugfix": {".ai/workflow.md", ".ai/testing.md"},
    "documentation": {".ai/documentation.md", "docs/foundation/guides/README.md"},
    "feature": {
        ".ai/workflow.md", ".ai/architecture.md", ".ai/coding-rules.md", ".ai/testing.md",
    },
    "refactor": {".ai/architecture.md", ".ai/coding-rules.md", ".ai/testing.md"},
    "release": {".ai/release.md", ".ai/security.md"},
    "requirements": {
        ".ai/mission.md", ".ai/documentation.md", "docs/foundation/templates/requirements.md",
    },
    "review": {".ai/review-checklist.md"},
    "security": {".ai/security.md", "SECURITY.md"},
    "test": {".ai/testing.md", ".ai/coding-rules.md"},
}


@dataclass(frozen=True)
class Counts:
    bytes: int = 0
    words: int = 0

    def __add__(self, other: "Counts") -> "Counts":
        return Counts(self.bytes + other.bytes, self.words + other.words)


def count_file(path: Path) -> Counts:
    content = path.read_text(encoding="utf-8")
    return Counts(len(content.encode("utf-8")), len(content.split()))


def parse_reads(skill_file: Path) -> list[str]:
    match = READS_PATTERN.search(skill_file.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"{skill_file}: missing one-line reads declaration")
    return [value.strip() for value in match.group(1).split(",") if value.strip()]


def route_path_error(root: Path, value: str) -> str | None:
    route_path = PurePosixPath(value)
    if route_path.is_absolute() or ".." in route_path.parts:
        return "must be a repository-relative path without traversal"
    if value.endswith("/") or any(character in value for character in GLOB_CHARACTERS):
        return "must name one file, not a directory or glob"
    resolved = root / route_path
    try:
        canonical = resolved.resolve(strict=True)
    except OSError:
        return "does not exist as a readable file"
    if not canonical.is_relative_to(root.resolve()):
        return "must not resolve outside the repository"
    if canonical.is_dir():
        return "must name one file, not a directory"
    if not canonical.is_file():
        return "does not exist as a readable file"
    return None


def budget_findings(
    label: str,
    actual: Counts,
    limit: Counts,
    *,
    enforce: bool,
) -> tuple[list[str], list[str]]:
    exceeded = []
    if actual.bytes > limit.bytes:
        exceeded.append(f"{actual.bytes} bytes > {limit.bytes}")
    if actual.words > limit.words:
        exceeded.append(f"{actual.words} words > {limit.words}")
    if not exceeded:
        return [], []
    message = f"{label} context budget exceeded: {', '.join(exceeded)}"
    return ([message], []) if enforce else ([], [message])


def measure_skill_route(
    root: Path,
    name: str,
    skill_file: Path,
    baseline: Counts,
) -> tuple[list[str], Counts]:
    errors: list[str] = []
    try:
        reads = parse_reads(skill_file)
    except (OSError, UnicodeError, ValueError) as error:
        return [str(error)], baseline

    duplicate_reads = sorted(
        value for value, count in Counter(reads).items() if count > 1
    )
    if duplicate_reads:
        errors.append(f"{skill_file}: duplicate reads: {duplicate_reads}")

    baseline_duplicates = sorted(set(BASELINE_FILES) & set(reads))
    if baseline_duplicates:
        errors.append(
            f"{skill_file}: redundantly rereads baseline: {baseline_duplicates}"
        )

    missing_reads = sorted(REQUIRED_READS.get(name, set()) - set(reads))
    if missing_reads:
        errors.append(f"{skill_file}: missing mandatory reads: {missing_reads}")

    route = baseline + count_file(skill_file)
    for value in dict.fromkeys(reads):
        reason = route_path_error(root, value)
        if reason:
            errors.append(f"{skill_file}: {value}: {reason}")
            continue
        route += count_file(root / value)
    return errors, route


def audit(root: Path, *, enforce_budget: bool) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    warnings: list[str] = []
    baseline = Counts()
    for value in BASELINE_FILES:
        path = root / value
        if not path.is_file():
            errors.append(f"baseline file is missing: {value}")
            continue
        baseline += count_file(path)

    budget_errors, budget_warnings = budget_findings(
        "baseline",
        baseline,
        Counts(BASELINE_BYTE_LIMIT, BASELINE_WORD_LIMIT),
        enforce=enforce_budget,
    )
    errors.extend(budget_errors)
    warnings.extend(budget_warnings)

    skill_directory = root / ".skills"
    skill_files = sorted(skill_directory.glob("*.skill.md"))
    actual_skills = {
        path.name.removesuffix(".skill.md"): path for path in skill_files
    }
    for missing_skill in sorted(REQUIRED_READS.keys() - actual_skills.keys()):
        errors.append(f"required skill is missing: {missing_skill}")

    largest_name = ""
    largest = Counts()
    for name, skill_file in actual_skills.items():
        route_errors, route = measure_skill_route(root, name, skill_file, baseline)
        errors.extend(route_errors)

        if route.bytes > largest.bytes:
            largest_name = name
            largest = route

        route_errors, route_warnings = budget_findings(
            f"{name} declared route",
            route,
            Counts(ROUTE_BYTE_LIMIT, ROUTE_WORD_LIMIT),
            enforce=enforce_budget,
        )
        errors.extend(route_errors)
        warnings.extend(route_warnings)

    report = {
        "baseline": baseline,
        "largest_route_name": largest_name,
        "largest_route": largest,
        "skill_count": len(skill_files),
        "budget_mode": "enforced" if enforce_budget else "reported",
    }
    return errors, warnings, report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("--root", type=Path, default=Path("."))
    validate.add_argument("--enforce-budget", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        errors, warnings, report = audit(
            args.root.resolve(),
            enforce_budget=args.enforce_budget,
        )
    except (OSError, UnicodeError) as error:
        print(f"context budget: ERROR: {error}", file=sys.stderr)
        return 2

    baseline = report["baseline"]
    largest = report["largest_route"]
    print(
        "context budget: "
        f"baseline={baseline.bytes}/{BASELINE_BYTE_LIMIT} bytes, "
        f"{baseline.words}/{BASELINE_WORD_LIMIT} words; "
        f"largest={report['largest_route_name']} "
        f"{largest.bytes}/{ROUTE_BYTE_LIMIT} bytes, "
        f"{largest.words}/{ROUTE_WORD_LIMIT} words; "
        f"skills={report['skill_count']}; mode={report['budget_mode']}"
    )
    for warning in warnings:
        print(f"context budget: WARNING: {warning}")
    for error in errors:
        print(f"context budget: ERROR: {error}", file=sys.stderr)
    if errors:
        return 2
    print("context budget: OK — declared routes preserve required files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
