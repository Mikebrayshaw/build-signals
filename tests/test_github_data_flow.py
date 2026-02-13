import unittest
from pathlib import Path

from scripts.supabase_loader import load_jsonl_file, normalize_record


class GithubDataFlowTests(unittest.TestCase):
    def test_matched_repos_survive_into_github_data(self):
        fixture = Path("docs/tests/matched_repo_fixture.jsonl")
        records = load_jsonl_file(fixture)

        self.assertEqual(len(records), 1)
        normalized = normalize_record(records[0])

        self.assertIn("github_data", normalized)
        self.assertIsInstance(normalized["github_data"], list)
        self.assertEqual(normalized["github_data"][0]["name"], "flagsmith/flagsmith")
        self.assertEqual(
            normalized["github_data"][0]["url"],
            "https://github.com/flagsmith/flagsmith",
        )
        self.assertEqual(
            normalized["github_url"],
            "https://github.com/flagsmith/flagsmith",
        )

    def test_backward_compat_for_legacy_github_field(self):
        legacy = {
            "id": "abc",
            "source": "hn_show",
            "title": "Show HN: Legacy payload",
            "github": [{"name": "org/repo", "url": "https://github.com/org/repo"}],
        }

        normalized = normalize_record(legacy)

        self.assertEqual(normalized["github_data"], legacy["github"])
        self.assertEqual(normalized["github_url"], "https://github.com/org/repo")


if __name__ == "__main__":
    unittest.main()
