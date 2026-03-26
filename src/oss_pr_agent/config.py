from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class AppConfig:
    query: str
    limit: int = 10
    output_dir: str = "out"
    log_dir: str = "out/logs"
    min_score: int = 45
    issue_labels: List[str] = field(default_factory=lambda: ["good first issue", "help wanted"])
    max_open_issues_per_repo: int = 5
    max_comments_per_issue: int = 10
    allow_missing_contributing: bool = False
    require_recent_activity_days: int = 120

    @classmethod
    def from_path(cls, path: str) -> "AppConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**data)
