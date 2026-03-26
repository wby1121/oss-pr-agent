from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


@dataclass
class ScoreCard:
    score: int
    accepted: bool
    reasons: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)


def _days_since(timestamp: str) -> int:
    updated_at = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    return (now - updated_at).days


def score_repository(
    repo: Dict,
    has_contributing: bool,
    allow_missing_contributing: bool,
    recent_days_limit: int,
    min_score: int,
) -> ScoreCard:
    score = 0
    reasons: List[str] = []
    risks: List[str] = []

    if repo.get("archived"):
        risks.append("Repository is archived.")
        return ScoreCard(score=0, accepted=False, reasons=reasons, risks=risks)

    stars = repo.get("stargazers_count", 0)
    open_issues = repo.get("open_issues_count", 0)
    days_since_push = _days_since(repo["pushed_at"])

    if stars >= 1000:
        score += 20
        reasons.append("Strong community signal from star count.")
    elif stars >= 200:
        score += 12
        reasons.append("Healthy star count for an MVP contribution target.")
    elif stars >= 50:
        score += 6
        reasons.append("Moderate community signal.")
    else:
        risks.append("Low star count may indicate lower maintainer throughput or immature project fit.")

    if open_issues > 0:
        score += 10
        reasons.append("Repository has open issues to target.")
    else:
        risks.append("No open issues detected.")

    if has_contributing:
        score += 12
        reasons.append("Contribution guide detected.")
    else:
        risks.append("No CONTRIBUTING guide detected.")

    if days_since_push <= 14:
        score += 20
        reasons.append("Very recently active repository.")
    elif days_since_push <= recent_days_limit:
        score += 12
        reasons.append("Recently maintained repository.")
    else:
        risks.append(f"Repository appears stale: last push was {days_since_push} days ago.")

    if repo.get("fork"):
        risks.append("Repository is a fork, which often reduces the chance of useful unsolicited PRs.")
    else:
        score += 6
        reasons.append("Primary repository, not a fork.")

    if repo.get("has_issues"):
        score += 8
        reasons.append("Issues are enabled.")
    else:
        risks.append("Issues are disabled.")

    accepted = score >= min_score and (has_contributing or allow_missing_contributing)
    return ScoreCard(score=score, accepted=accepted, reasons=reasons, risks=risks)
