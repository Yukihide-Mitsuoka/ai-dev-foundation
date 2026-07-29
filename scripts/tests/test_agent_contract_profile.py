import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "template_inheritance.py"
SPEC = importlib.util.spec_from_file_location("agent_contract_profile", MODULE_PATH)
inheritance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inheritance)

FOUNDATION = "acme/ai-foundation"
PARENT = "acme/stack-template"
PROJECT = "acme/product"
COMMIT = "a" * 40
PROFILE_PATH = ".github/inheritance/agent-profile.json"
FOUNDATION_ENTRY_PATH = ".ai/contracts/foundation/agent-entry.md"
REQUIRED_PROTECTED = [
    ".gitignore",
    ".github/governance/repository.json",
    ".github/inheritance/lock.json",
    ".github/inheritance/manifest.json",
    PROFILE_PATH,
    ".github/workflows/template-sync.yml",
    ".templatesyncignore",
    ".ai/project/",
]


def profile_input(layer, repository, path):
    return {"layer": layer, "repository": repository, "path": path}


class AgentContractProfileTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name) / "child"
        self.root.mkdir()

    def write(self, relative_path, content):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_contract(self, *, parent, inputs, inherited=None, protected=None):
        manifest = {
            "schema_version": 2,
            "parent": {"repository": parent, "branch": "main"},
            "lock_file": ".github/inheritance/lock.json",
            "inherited_paths": inherited or [
                ".ai/contracts/foundation/",
                ".ai/contracts/templates/",
            ],
            "protected_paths": protected or REQUIRED_PROTECTED,
        }
        lock = {
            "schema_version": 1,
            "parent": {"repository": parent, "commit": COMMIT},
        }
        profile = {
            "schema_version": 1,
            "authority_policy": "strengthen-only",
            "inputs": inputs,
        }
        self.write(".github/inheritance/manifest.json", json.dumps(manifest))
        self.write(".github/inheritance/lock.json", json.dumps(lock))
        self.write(PROFILE_PATH, json.dumps(profile))
        self.write(
            ".templatesyncignore",
            "\n".join(manifest["protected_paths"] + [".github/workflows/**"]) + "\n",
        )
        for item in inputs:
            self.write(item["path"], f"{item['layer']} contract\n")

    def test_direct_child_reports_foundation_then_project(self):
        inputs = [
            profile_input(
                "foundation", FOUNDATION, ".ai/contracts/foundation/agent-entry.md"
            ),
            profile_input("project", PROJECT, ".ai/project/agent-overlay.md"),
        ]
        self.write_contract(parent=FOUNDATION, inputs=inputs)

        result = inheritance.validate_inheritance(self.root)

        self.assertEqual(result["agent_contract"]["inputs"], inputs)
        self.assertEqual(result["agent_contract"]["authority_policy"], "strengthen-only")

    def test_multi_level_child_preserves_parent_to_child_template_order(self):
        inputs = [
            profile_input(
                "foundation", FOUNDATION, ".ai/contracts/foundation/agent-entry.md"
            ),
            profile_input(
                "template",
                "acme/platform-template",
                ".ai/contracts/templates/acme/platform-template/agent-overlay.md",
            ),
            profile_input(
                "template",
                PARENT,
                ".ai/contracts/templates/acme/stack-template/agent-overlay.md",
            ),
            profile_input("project", PROJECT, ".ai/project/agent-overlay.md"),
        ]
        self.write_contract(parent=PARENT, inputs=inputs)

        result = inheritance.validate_inheritance(self.root)

        self.assertEqual(
            [item["repository"] for item in result["agent_contract"]["inputs"]],
            [FOUNDATION, "acme/platform-template", PARENT, PROJECT],
        )

    def test_profile_rejects_unsafe_authority_order_or_policy(self):
        valid_inputs = [
            profile_input(
                "foundation", FOUNDATION, ".ai/contracts/foundation/agent-entry.md"
            ),
            profile_input("project", PROJECT, ".ai/project/agent-overlay.md"),
        ]
        cases = (
            list(reversed(valid_inputs)),
            valid_inputs
            + [
                profile_input(
                    "template",
                    PARENT,
                    ".ai/contracts/templates/acme/stack-template/agent-overlay.md",
                )
            ],
        )
        for inputs in cases:
            with self.subTest(inputs=inputs):
                self.write_contract(parent=FOUNDATION, inputs=inputs)
                with self.assertRaisesRegex(inheritance.InheritanceError, "order"):
                    inheritance.validate_inheritance(self.root)

        self.write_contract(parent=FOUNDATION, inputs=valid_inputs)
        profile = json.loads((self.root / PROFILE_PATH).read_text(encoding="utf-8"))
        profile["authority_policy"] = "last-wins"
        self.write(PROFILE_PATH, json.dumps(profile))
        with self.assertRaisesRegex(inheritance.InheritanceError, "strengthen-only"):
            inheritance.validate_inheritance(self.root)

    def test_profile_rejects_missing_or_misowned_references(self):
        inputs = [
            profile_input(
                "foundation", FOUNDATION, ".ai/contracts/foundation/agent-entry.md"
            ),
            profile_input("project", PROJECT, ".ai/project/agent-overlay.md"),
        ]
        self.write_contract(parent=FOUNDATION, inputs=inputs)
        (self.root / inputs[0]["path"]).unlink()
        with self.assertRaisesRegex(inheritance.InheritanceError, "must be a file"):
            inheritance.validate_inheritance(self.root)

        self.write_contract(
            parent=FOUNDATION,
            inputs=inputs,
            inherited=["scripts/"],
        )
        with self.assertRaisesRegex(inheritance.InheritanceError, "must be inherited"):
            inheritance.validate_inheritance(self.root)

    def test_template_overlay_is_owner_qualified_and_ends_at_direct_parent(self):
        inputs = [
            profile_input(
                "foundation", FOUNDATION, ".ai/contracts/foundation/agent-entry.md"
            ),
            profile_input(
                "template",
                "acme/other-template",
                ".ai/contracts/templates/acme/other-template/agent-overlay.md",
            ),
            profile_input("project", PROJECT, ".ai/project/agent-overlay.md"),
        ]
        self.write_contract(parent=PARENT, inputs=inputs)
        with self.assertRaisesRegex(inheritance.InheritanceError, "direct parent"):
            inheritance.validate_inheritance(self.root)

        inputs[1]["repository"] = PARENT
        inputs[1]["path"] = ".ai/contracts/templates/wrong/path/agent-overlay.md"
        self.write_contract(parent=PARENT, inputs=inputs)
        with self.assertRaisesRegex(inheritance.InheritanceError, "owner-qualified"):
            inheritance.validate_inheritance(self.root)


class FoundationAgentEntryTest(unittest.TestCase):
    def test_entry_is_identity_free_and_routes_required_foundation_context(self):
        root = Path(__file__).parents[2]
        entry_path = root / FOUNDATION_ENTRY_PATH

        self.assertTrue(entry_path.is_file(), f"missing {FOUNDATION_ENTRY_PATH}")
        content = entry_path.read_text(encoding="utf-8")
        for project_identity in (
            "{{PROJECT_NAME}}",
            "{{STACK}}",
            "Yukihide-Mitsuoka",
            "ai-dev-foundation",
        ):
            self.assertNotIn(project_identity, content)
        for required_reference in (
            ".ai/guardrails.md",
            ".ai/README.md",
            "docs/development-handoff.md",
            "make format",
            "make lint",
            "foundation",
            "template",
            "project",
            "strengthen-only",
        ):
            with self.subTest(required_reference=required_reference):
                self.assertIn(required_reference, content)


if __name__ == "__main__":
    unittest.main()
