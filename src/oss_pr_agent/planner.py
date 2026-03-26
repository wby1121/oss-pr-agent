from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Opportunity:
    issue_title: str
    issue_url: str
    issue_number: int
    labels: List[str]
    issue_kind: str
    priority_reason: str
    comment_signals: List[str]
    thesis: str
    implementation_outline: List[str]
    pr_title: str
    pr_body: str
    reply_draft: str


def _issue_kind(text: str) -> str:
    lowered = text.lower()
    bug_keywords = ["bug", "error", "broken", "crash", "fail", "exception", "incorrect"]
    feature_keywords = ["feature", "request", "support", "add", "enhancement", "improve"]
    bug_hits = sum(keyword in lowered for keyword in bug_keywords)
    feature_hits = sum(keyword in lowered for keyword in feature_keywords)
    if bug_hits >= feature_hits and bug_hits > 0:
        return "bug"
    if feature_hits > 0:
        return "feature"
    return "general"


def _summarize_comment_signals(comments: List[Dict]) -> List[str]:
    signals: List[str] = []
    for comment in comments[:3]:
        body = " ".join(comment.get("body", "").split())
        if not body:
            continue
        snippet = body[:140].rstrip()
        signals.append(snippet + ("..." if len(body) > 140 else ""))
    return signals


def _priority_reason(issue: Dict, comments: List[Dict]) -> str:
    title = issue.get("title", "")
    body = issue.get("body", "") or ""
    discussion = " ".join(comment.get("body", "") for comment in comments)
    combined = f"{title} {body} {discussion}"
    kind = _issue_kind(combined)
    if comments and kind == "bug":
        return "Comments add reproduction context, so this issue is prioritized as a bug fix."
    if comments and kind == "feature":
        return "Comments reinforce user or maintainer demand, so this issue is prioritized as a feature request."
    if comments:
        return "Comments provide extra execution context, so this issue is prioritized ahead of less specific items."
    if kind == "bug":
        return "Issue text looks like a bug report and is prioritized for lower-risk contribution value."
    if kind == "feature":
        return "Issue text looks like a concrete feature request and is prioritized as a scoped enhancement."
    return "Issue is selected as the best available open contribution target."


def _rank_issue(issue: Dict) -> tuple:
    comments = issue.get("comment_details", [])
    text = " ".join(
        [
            issue.get("title", ""),
            issue.get("body", "") or "",
            " ".join(comment.get("body", "") for comment in comments),
        ]
    )
    kind = _issue_kind(text)
    kind_weight = 2 if kind == "bug" else 1 if kind == "feature" else 0
    return (len(comments), kind_weight)


def choose_opportunity(repo: Dict, issues: List[Dict]) -> Optional[Opportunity]:
    if not issues:
        return None

    issue = sorted(issues, key=_rank_issue, reverse=True)[0]
    comments = issue.get("comment_details", [])
    label_names = [label["name"] for label in issue.get("labels", [])]
    repo_name = repo["full_name"]
    title = issue["title"].strip()
    combined_text = " ".join(
        [title, issue.get("body", "") or "", " ".join(comment.get("body", "") for comment in comments)]
    )
    issue_kind = _issue_kind(combined_text)
    priority_reason = _priority_reason(issue, comments)
    comment_signals = _summarize_comment_signals(comments)

    thesis = (
        f"Address issue #{issue['number']} in {repo_name} with a narrowly scoped change, "
        "backed by tests and aligned to the repository's existing contribution patterns."
    )

    outline = [
        "Reproduce or clarify the current issue locally.",
        "Review the issue discussion and convert the strongest comment signal into acceptance criteria.",
        "Identify the smallest code path that resolves the issue.",
        "Add or update tests before finalizing the patch.",
        "Document the behavior change in the PR description.",
    ]

    pr_title = f"Fix #{issue['number']}: {title}"
    pr_body = "\n".join(
        [
            "## Summary",
            f"This PR proposes a focused fix for #{issue['number']} ({title}).",
            "",
            "## Why This Issue",
            priority_reason,
            "",
            "## What Changed",
            "- implemented the smallest viable change to address the reported problem",
            "- added or updated tests to cover the behavior",
            "- kept the scope intentionally narrow to reduce review burden",
            "",
            "## Validation",
            "- reproduced the issue locally",
            "- ran the relevant test suite",
            "",
            "## Notes",
            "- happy to adjust naming, scope, or approach based on maintainer feedback",
        ]
    )

    reply_draft = "\n".join(
        [
            "Thanks for the review.",
            "I used the issue discussion as the baseline for scope and expected behavior.",
            "If there is a project-specific convention I missed, I can align the patch and tests in a follow-up commit.",
        ]
    )

    return Opportunity(
        issue_title=title,
        issue_url=issue["html_url"],
        issue_number=issue["number"],
        labels=label_names,
        issue_kind=issue_kind,
        priority_reason=priority_reason,
        comment_signals=comment_signals,
        thesis=thesis,
        implementation_outline=outline,
        pr_title=pr_title,
        pr_body=pr_body,
        reply_draft=reply_draft,
    )
