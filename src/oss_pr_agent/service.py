from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from .config import AppConfig
from .github_api import GitHubClient
from .planner import Opportunity, choose_opportunity
from .scoring import ScoreCard, score_repository


@dataclass
class Candidate:
    issue_number: int
    title: str
    url: str
    kind: str
    labels: List[str]
    comments_count: int
    priority_reason: str
    comment_signals: List[str]


@dataclass
class InspectionResult:
    repo: Dict
    scorecard: ScoreCard
    candidates: List[Candidate]
    recommended: Optional[Opportunity]


def parse_repo_url(repo_url: str) -> str:
    match = re.search(r"github\.com/([^/\s]+)/([^/\s#?]+)", repo_url.strip())
    if not match:
        raise ValueError("Unsupported GitHub repository URL.")
    owner, repo = match.groups()
    return f"{owner}/{repo.removesuffix('.git')}"


def _candidate_from_opportunity(opportunity: Opportunity, comments_count: int) -> Candidate:
    return Candidate(
        issue_number=opportunity.issue_number,
        title=opportunity.issue_title,
        url=opportunity.issue_url,
        kind=opportunity.issue_kind,
        labels=opportunity.labels,
        comments_count=comments_count,
        priority_reason=opportunity.priority_reason,
        comment_signals=opportunity.comment_signals,
    )


class RepoInspector:
    def __init__(self, config: AppConfig, client: GitHubClient) -> None:
        self.config = config
        self.client = client

    def inspect_repository(self, repo_url: str) -> InspectionResult:
        full_name = parse_repo_url(repo_url)
        repo = self.client.get_repository(full_name)
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

        candidates: List[Candidate] = []
        for issue in issues:
            opportunity = choose_opportunity(repo, [issue])
            if opportunity:
                candidates.append(_candidate_from_opportunity(opportunity, len(issue.get("comment_details", []))))

        candidates.sort(key=lambda item: (item.comments_count, item.kind == "bug"), reverse=True)
        recommended = choose_opportunity(repo, issues)
        return InspectionResult(repo=repo, scorecard=scorecard, candidates=candidates, recommended=recommended)

    @staticmethod
    def serialize(result: InspectionResult) -> Dict:
        repo = result.repo
        return {
            "repo": {
                "full_name": repo["full_name"],
                "html_url": repo["html_url"],
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stargazers_count": repo.get("stargazers_count", 0),
                "open_issues_count": repo.get("open_issues_count", 0),
                "default_branch": repo.get("default_branch"),
                "pushed_at": repo.get("pushed_at"),
            },
            "scorecard": asdict(result.scorecard),
            "candidates": [asdict(candidate) for candidate in result.candidates],
            "recommended": asdict(result.recommended) if result.recommended else None,
        }
