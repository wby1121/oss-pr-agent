from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .config import AppConfig
from .github_api import GitHubClient
from .planner import choose_opportunity
from .renderer import write_bundle, write_run_log
from .scoring import ScoreCard, score_repository


@dataclass
class EvaluatedRepo:
    repo: Dict
    scorecard: ScoreCard
    issues: List[Dict]


class Workflow:
    def __init__(self, config: AppConfig, client: GitHubClient) -> None:
        self.config = config
        self.client = client

    def discover(self, override_query: str = "") -> List[EvaluatedRepo]:
        query = override_query or self.config.query
        repos = self.client.search_repositories(query=query, limit=self.config.limit)
        evaluated: List[EvaluatedRepo] = []
        for repo in repos:
            full_name = repo["full_name"]
            has_contributing = self.client.any_file_exists(
                full_name,
                ["CONTRIBUTING.md", "contributing.md", ".github/CONTRIBUTING.md"],
                repo["default_branch"],
            )
            scorecard = score_repository(
                repo=repo,
                has_contributing=has_contributing,
                allow_missing_contributing=self.config.allow_missing_contributing,
                recent_days_limit=self.config.require_recent_activity_days,
                min_score=self.config.min_score,
            )
            issues = []
            if scorecard.accepted:
                issues = self.client.search_issues(
                    full_name=full_name,
                    labels=self.config.issue_labels,
                    limit=self.config.max_open_issues_per_repo,
                )
                for issue in issues:
                    issue["comment_details"] = self.client.issue_comments(
                        full_name=full_name,
                        issue_number=issue["number"],
                        limit=self.config.max_comments_per_issue,
                    )
            evaluated.append(EvaluatedRepo(repo=repo, scorecard=scorecard, issues=issues))
        evaluated.sort(key=lambda item: item.scorecard.score, reverse=True)
        return evaluated

    def draft(self, override_query: str = "", limit: int = 0) -> Dict[str, List[str]]:
        evaluated = self.discover(override_query=override_query)
        selected = [item for item in evaluated if item.scorecard.accepted][: limit or self.config.limit]
        written_paths: List[str] = []
        log_items: List[Dict] = []
        for item in selected:
            opportunity = choose_opportunity(item.repo, item.issues)
            bundle_dir = write_bundle(
                output_root=self.config.output_dir,
                repo=item.repo,
                scorecard=item.scorecard,
                issues=item.issues,
                opportunity=opportunity,
            )
            written_paths.append(str(bundle_dir))
            log_items.append(
                {
                    "repo": item.repo,
                    "score": item.scorecard.score,
                    "bundle_dir": str(bundle_dir),
                    "opportunity": opportunity,
                }
            )
        log_path = write_run_log(self.config.log_dir, log_items)
        return {"bundles": written_paths, "log_path": [str(log_path)]}
