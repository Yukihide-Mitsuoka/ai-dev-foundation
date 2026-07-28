import unittest

from scripts.pr_size_policy import evaluate_size, summarize_lockfiles


class PullRequestSizePolicyTests(unittest.TestCase):
    def test_excludes_lockfile_churn_from_hard_limit(self) -> None:
        lockfile_stats = summarize_lockfiles(
            [
                {"filename": "package.json", "additions": 15, "deletions": 58},
                {"filename": "pnpm-lock.yaml", "additions": 300, "deletions": 700},
            ]
        )

        result = evaluate_size(315, 758, 2, lockfile_stats)

        self.assertEqual(result.changed_lines, 73)
        self.assertEqual(result.changed_files, 1)
        self.assertEqual(result.level, "ok")


if __name__ == "__main__":
    unittest.main()
