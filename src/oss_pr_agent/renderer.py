from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .planner import Opportunity
from .scoring import ScoreCard


def slugify(value: str) -> str:
    allowed = []
    for char in value.lower():
        if char.isalnum():
            allowed.append(char)
        elif char in {"-", "_", "/"}:
            allowed.append("-")
    return "".join(allowed).strip("-")


def write_bundle(
    output_root: str,
    repo: Dict,
    scorecard: ScoreCard,
    issues: List[Dict],
    opportunity: Optional[Opportunity],
) -> Path:
    bundle_dir = Path(output_root) / slugify(repo["full_name"])
    bundle_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "repository": {
            "name": repo["full_name"],
            "url": repo["html_url"],
            "description": repo.get("description"),
            "language": repo.get("language"),
            "stars": repo.get("stargazers_count"),
            "open_issues": repo.get("open_issues_count"),
            "default_branch": repo.get("default_branch"),
            "pushed_at": repo.get("pushed_at"),
        },
        "score": scorecard.score,
        "accepted": scorecard.accepted,
        "reasons": scorecard.reasons,
        "risks": scorecard.risks,
        "issues_considered": [
            {
                "number": issue["number"],
                "title": issue["title"],
                "url": issue["html_url"],
            }
            for issue in issues
        ],
        "selected_opportunity": (
            {
                "issue_number": opportunity.issue_number,
                "issue_title": opportunity.issue_title,
                "issue_url": opportunity.issue_url,
                "labels": opportunity.labels,
                "issue_kind": opportunity.issue_kind,
                "priority_reason": opportunity.priority_reason,
                "comment_signals": opportunity.comment_signals,
            }
            if opportunity
            else None
        ),
    }

    (bundle_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    analysis_lines = [
        f"# {repo['full_name']}",
        "",
        f"- URL: {repo['html_url']}",
        f"- Language: {repo.get('language')}",
        f"- Stars: {repo.get('stargazers_count')}",
        f"- Open issues: {repo.get('open_issues_count')}",
        f"- Score: {scorecard.score}",
        f"- Accepted: {scorecard.accepted}",
        "",
        "## Reasons",
    ]
    analysis_lines.extend([f"- {reason}" for reason in scorecard.reasons] or ["- None"])
    analysis_lines.extend(["", "## Risks"])
    analysis_lines.extend([f"- {risk}" for risk in scorecard.risks] or ["- None"])
    (bundle_dir / "analysis.md").write_text("\n".join(analysis_lines) + "\n", encoding="utf-8")

    if opportunity:
        task_lines = [
            f"# Opportunity: {opportunity.issue_title}",
            "",
            f"- Issue: {opportunity.issue_url}",
            f"- Labels: {', '.join(opportunity.labels) if opportunity.labels else 'none'}",
            f"- Kind: {opportunity.issue_kind}",
            "",
            "## Thesis",
            opportunity.thesis,
            "",
            "## Priority Reason",
            opportunity.priority_reason,
            "",
            "## Comment Signals",
        ]
        task_lines.extend([f"- {item}" for item in opportunity.comment_signals] or ["- No recent comment signal captured."])
        task_lines.extend(["", "## Implementation Outline"])
        task_lines.extend([f"- {item}" for item in opportunity.implementation_outline])
        (bundle_dir / "task.md").write_text("\n".join(task_lines) + "\n", encoding="utf-8")
        (bundle_dir / "pr_draft.md").write_text(
            f"# {opportunity.pr_title}\n\n{opportunity.pr_body}\n",
            encoding="utf-8",
        )
        (bundle_dir / "reply_draft.md").write_text(opportunity.reply_draft + "\n", encoding="utf-8")

    return bundle_dir


def write_run_log(output_root: str, selected_runs: List[Dict]) -> Path:
    log_dir = Path(output_root)
    log_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    log_path = log_dir / f"run-{now.strftime('%Y%m%d-%H%M%S')}.md"

    lines = [
        "# OSS PR Agent Run Log",
        "",
        f"- Generated at: {now.isoformat(timespec='seconds')}",
        f"- Repositories processed: {len(selected_runs)}",
        "",
    ]

    if not selected_runs:
        lines.extend(["No accepted repositories were drafted in this run.", ""])
    else:
        for index, item in enumerate(selected_runs, start=1):
            repo = item["repo"]
            opportunity = item.get("opportunity")
            lines.extend(
                [
                    f"## {index}. {repo['full_name']}",
                    "",
                    f"- GitHub: {repo['html_url']}",
                    f"- Stars: {repo.get('stargazers_count', 0)}",
                    f"- Score: {item['score']}",
                    f"- Bundle: {item['bundle_dir']}",
                ]
            )
            if opportunity:
                lines.extend(
                    [
                        f"- Selected issue: #{opportunity.issue_number} {opportunity.issue_title}",
                        f"- Issue URL: {opportunity.issue_url}",
                        f"- Type: {opportunity.issue_kind}",
                        f"- Priority reason: {opportunity.priority_reason}",
                    ]
                )
                if opportunity.comment_signals:
                    lines.append("- Comment signals:")
                    for signal in opportunity.comment_signals:
                        lines.append(f"  - {signal}")
            else:
                lines.append("- Selected issue: none")
            lines.append("")

    log_path.write_text("\n".join(lines), encoding="utf-8")
    return log_path


def write_session_log(output_root: str, session: Dict) -> Path:
    log_dir = Path(output_root)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"session-{session['id']}.md"

    repo = session["repo"]
    solution = session.get("solution")
    drafts = session.get("drafts", {})
    submission = session.get("submission")

    lines = [
        "# OSS PR Agent Session Log",
        "",
        f"- Session ID: {session['id']}",
        f"- Status: {session['status']}",
        f"- GitHub: {repo['html_url']}",
        f"- Stars: {repo.get('stargazers_count', 0)}",
        "",
    ]

    if solution:
        lines.extend(
            [
                "## Selected Work",
                "",
                f"- Issue: #{solution['issue_number']} {solution['issue_title']}",
                f"- Issue URL: {solution['issue_url']}",
                f"- Type: {solution['issue_kind']}",
                f"- Priority: {solution['priority_reason']}",
                "",
                "## Solution Outline",
            ]
        )
        for item in solution["implementation_outline"]:
            lines.append(f"- {item}")
        lines.append("")

    if drafts:
        lines.extend(
            [
                "## PR Draft",
                "",
                f"### {drafts.get('pr_title', '')}",
                "",
                drafts.get("pr_body", ""),
                "",
                "## Reply Draft",
                "",
                drafts.get("reply_body", ""),
                "",
            ]
        )

    if submission:
        lines.extend(
            [
                "## Submission",
                "",
                f"- Branch: {submission['branch_name']}",
                f"- State: {submission['state']}",
                f"- Summary file: {submission['path']}",
                "",
            ]
        )

    log_path.write_text("\n".join(lines), encoding="utf-8")
    return log_path
