from __future__ import annotations

import argparse
import sys
from typing import Iterable

from .config import AppConfig
from .github_api import GitHubAPIError, GitHubClient
from .webapp import run_server
from .workflow import Workflow


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dry-run MVP for AI-assisted OSS PR scouting.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config", required=True, help="Path to JSON config file.")
    common.add_argument("--query", default="", help="Optional query override.")
    common.add_argument("--limit", type=int, default=0, help="Optional result limit override.")

    subparsers.add_parser("discover", parents=[common], help="Search and score repositories.")
    subparsers.add_parser("draft", parents=[common], help="Generate local contribution bundles.")
    web_parser = subparsers.add_parser("web", parents=[common], help="Run the local web UI.")
    web_parser.add_argument("--host", default="127.0.0.1", help="Host to bind the local web server.")
    web_parser.add_argument("--port", type=int, default=8000, help="Port to bind the local web server.")
    return parser


def _print_discovery(rows: Iterable) -> None:
    for index, item in enumerate(rows, start=1):
        repo = item.repo
        print(
            f"{index}. {repo['full_name']} | score={item.scorecard.score} | "
            f"stars={repo.get('stargazers_count', 0)} | issues={len(item.issues)} | "
            f"accepted={item.scorecard.accepted}"
        )
        if item.scorecard.risks:
            print(f"   risks: {'; '.join(item.scorecard.risks)}")


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    config = AppConfig.from_path(args.config)
    if args.limit:
        config.limit = args.limit

    workflow = Workflow(config=config, client=GitHubClient())

    try:
        if args.command == "discover":
            rows = workflow.discover(override_query=args.query)
            _print_discovery(rows)
            return
        if args.command == "draft":
            result = workflow.draft(override_query=args.query, limit=args.limit)
            print("Generated bundles:")
            for path in result["bundles"]:
                print(f"- {path}")
            print("Generated log:")
            for path in result["log_path"]:
                print(f"- {path}")
            return
        if args.command == "web":
            run_server(config=config, host=args.host, port=args.port)
            return
    except GitHubAPIError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
