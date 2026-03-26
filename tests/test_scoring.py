import unittest

from oss_pr_agent.planner import choose_opportunity
from oss_pr_agent.renderer import slugify
from oss_pr_agent.scoring import score_repository


class ScoringTests(unittest.TestCase):
    def test_missing_contributing_blocks_acceptance_when_required(self) -> None:
        repo = {
            "archived": False,
            "stargazers_count": 1200,
            "open_issues_count": 12,
            "pushed_at": "2026-03-20T10:00:00Z",
            "fork": False,
            "has_issues": True,
        }
        card = score_repository(
            repo=repo,
            has_contributing=False,
            allow_missing_contributing=False,
            recent_days_limit=120,
            min_score=40,
        )
        self.assertFalse(card.accepted)
        self.assertIn("No CONTRIBUTING guide detected.", card.risks)

    def test_allow_missing_contributing_keeps_repo_eligible(self) -> None:
        repo = {
            "archived": False,
            "stargazers_count": 1200,
            "open_issues_count": 12,
            "pushed_at": "2026-03-20T10:00:00Z",
            "fork": False,
            "has_issues": True,
        }
        card = score_repository(
            repo=repo,
            has_contributing=False,
            allow_missing_contributing=True,
            recent_days_limit=120,
            min_score=40,
        )
        self.assertTrue(card.accepted)

    def test_slugify_normalizes_repo_name(self) -> None:
        self.assertEqual(slugify("OpenAI/Gym"), "openai-gym")

    def test_choose_opportunity_prioritizes_comment_backed_bug(self) -> None:
        repo = {"full_name": "owner/project"}
        issues = [
            {
                "number": 1,
                "title": "Add export option",
                "body": "Feature request",
                "html_url": "https://github.com/owner/project/issues/1",
                "labels": [{"name": "enhancement"}],
                "comment_details": [],
            },
            {
                "number": 2,
                "title": "Crash on startup",
                "body": "App crashes when config is empty",
                "html_url": "https://github.com/owner/project/issues/2",
                "labels": [{"name": "bug"}],
                "comment_details": [
                    {"body": "I can reproduce this on macOS, stack trace points to config loader."}
                ],
            },
        ]
        opportunity = choose_opportunity(repo, issues)
        self.assertIsNotNone(opportunity)
        self.assertEqual(opportunity.issue_number, 2)
        self.assertEqual(opportunity.issue_kind, "bug")
        self.assertTrue(opportunity.comment_signals)


if __name__ == "__main__":
    unittest.main()
