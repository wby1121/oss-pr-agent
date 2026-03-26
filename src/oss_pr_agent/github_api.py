from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List, Optional


class GitHubAPIError(RuntimeError):
    pass


class GitHubClient:
    def __init__(
        self,
        token: Optional[str] = None,
        user_agent: str = "oss-pr-agent/0.1.0",
        retries: int = 3,
    ) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.user_agent = user_agent
        self.retries = retries

    def _request(self, path: str, params: Optional[Dict[str, str]] = None) -> Dict:
        query = f"?{urllib.parse.urlencode(params)}" if params else ""
        url = f"https://api.github.com{path}{query}"
        request = urllib.request.Request(url)
        request.add_header("Accept", "application/vnd.github+json")
        request.add_header("User-Agent", self.user_agent)
        if self.token:
            request.add_header("Authorization", f"Bearer {self.token}")

        last_error: Optional[Exception] = None
        for attempt in range(1, self.retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                raise GitHubAPIError(f"GitHub API error {exc.code} for {url}: {body}") from exc
            except (urllib.error.URLError, ConnectionError, TimeoutError) as exc:
                last_error = exc
                if attempt == self.retries:
                    reason = getattr(exc, "reason", str(exc))
                    raise GitHubAPIError(f"GitHub API request failed for {url}: {reason}") from exc
                time.sleep(0.5 * attempt)
        reason = getattr(last_error, "reason", str(last_error))
        raise GitHubAPIError(f"GitHub API request failed for {url}: {reason}")

    def search_repositories(self, query: str, limit: int) -> List[Dict]:
        payload = self._request(
            "/search/repositories",
            {
                "q": query,
                "sort": "updated",
                "order": "desc",
                "per_page": str(min(limit, 100)),
            },
        )
        return payload.get("items", [])[:limit]

    def get_repository(self, full_name: str) -> Dict:
        payload = self._request(f"/repos/{full_name}")
        if not isinstance(payload, dict):
            raise GitHubAPIError(f"Unexpected repository payload for {full_name}")
        return payload

    def search_issues(self, full_name: str, labels: List[str], limit: int) -> List[Dict]:
        issue_results: List[Dict] = []
        seen = set()
        for label in labels:
            query = f'repo:{full_name} is:issue is:open label:"{label}" no:assignee'
            payload = self._request(
                "/search/issues",
                {
                    "q": query,
                    "sort": "updated",
                    "order": "desc",
                    "per_page": str(min(limit, 20)),
                },
            )
            for item in payload.get("items", []):
                if item["id"] in seen:
                    continue
                issue_results.append(item)
                seen.add(item["id"])
        if not issue_results:
            fallback_query = f"repo:{full_name} is:issue is:open no:assignee comments:>0"
            payload = self._request(
                "/search/issues",
                {
                    "q": fallback_query,
                    "sort": "updated",
                    "order": "desc",
                    "per_page": str(min(limit, 20)),
                },
            )
            for item in payload.get("items", []):
                if item["id"] in seen:
                    continue
                issue_results.append(item)
                seen.add(item["id"])
        if not issue_results:
            broad_query = f"repo:{full_name} is:issue is:open no:assignee"
            payload = self._request(
                "/search/issues",
                {
                    "q": broad_query,
                    "sort": "updated",
                    "order": "desc",
                    "per_page": str(min(limit, 20)),
                },
            )
            for item in payload.get("items", []):
                if item["id"] in seen:
                    continue
                issue_results.append(item)
                seen.add(item["id"])
        return issue_results[:limit]

    def issue_comments(self, full_name: str, issue_number: int, limit: int) -> List[Dict]:
        payload = self._request(
            f"/repos/{full_name}/issues/{issue_number}/comments",
            {"per_page": str(min(limit, 100)), "sort": "updated", "direction": "desc"},
        )
        if isinstance(payload, list):
            return payload[:limit]
        return []

    def file_exists(self, full_name: str, path: str, default_branch: str) -> bool:
        try:
            self._request(f"/repos/{full_name}/contents/{path}", {"ref": default_branch})
            return True
        except GitHubAPIError as exc:
            if "error 404" in str(exc):
                return False
            raise

    def any_file_exists(self, full_name: str, paths: List[str], default_branch: str) -> bool:
        for path in paths:
            if self.file_exists(full_name, path, default_branch):
                return True
        return False
