import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def python_analysis_is_enabled(workflow: str) -> bool:
    return "language: [python]" in workflow and "language: []" not in workflow


class CodeQLWorkflowTest(unittest.TestCase):
    def test_python_analysis_is_enabled(self) -> None:
        workflow = (ROOT / ".github/workflows/codeql.yml").read_text()

        self.assertTrue(python_analysis_is_enabled(workflow))

    def test_python_analysis_can_share_a_multi_language_matrix(self) -> None:
        workflow = "matrix:\n  language: [javascript-typescript, python]\n"

        self.assertTrue(python_analysis_is_enabled(workflow))


if __name__ == "__main__":
    unittest.main()
