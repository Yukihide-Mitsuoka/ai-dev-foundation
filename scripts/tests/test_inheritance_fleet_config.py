import json
import unittest
from pathlib import Path


CONFIG_PATH = Path(__file__).parents[1] / "inheritance-fleet.json"


class InheritanceFleetConfigTest(unittest.TestCase):
    def test_canonical_fleet_contains_every_active_relationship_once(self):
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

        self.assertEqual(config["schema_version"], 1)
        self.assertEqual(
            config["retired_repositories"], ["Yukihide-Mitsuoka/chat-chart"]
        )
        self.assertEqual(
            {
                (
                    item["repository"],
                    item["directory"],
                    item["parent_repository"],
                    item["parent_directory"],
                )
                for item in config["repositories"]
            },
            {
                (
                    "Yukihide-Mitsuoka/terraform-gcp-template",
                    "terraform-gcp-template",
                    "Yukihide-Mitsuoka/ai-dev-foundation",
                    "ai-dev-foundation",
                ),
                (
                    "Yukihide-Mitsuoka/nextjs-saas-template",
                    "nextjs-saas-template",
                    "Yukihide-Mitsuoka/ai-dev-foundation",
                    "ai-dev-foundation",
                ),
                (
                    "Yukihide-Mitsuoka/repchat",
                    "repchat",
                    "Yukihide-Mitsuoka/ai-dev-foundation",
                    "ai-dev-foundation",
                ),
                (
                    "Yukihide-Mitsuoka/secure-ga4-bq-template",
                    "secure-ga4-bq-template",
                    "Yukihide-Mitsuoka/terraform-gcp-template",
                    "terraform-gcp-template",
                ),
                (
                    "ea-Mitsuoka/secure-ai-controls",
                    "secure-ai-controls",
                    "Yukihide-Mitsuoka/terraform-gcp-template",
                    "terraform-gcp-template",
                ),
            },
        )
        self.assertEqual(len(config["repositories"]), 5)


if __name__ == "__main__":
    unittest.main()
