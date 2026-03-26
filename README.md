# OSS PR Agent

<p align="center">
  <strong>A local-first AI workspace for discovering OSS issues, drafting contribution plans, and preparing PR-ready artifacts.</strong>
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="./README.zh-CN.md">简体中文</a> ·
  <a href="./README.ja.md">日本語</a> ·
  <a href="./README.ko.md">한국어</a> ·
  <a href="./README.ru.md">Русский</a>
</p>

<p align="center">
  <code>Python 3.9+</code>
  <code>Local-first</code>
  <code>Markdown workflow</code>
  <code>Web UI</code>
</p>

## Overview

`OSS PR Agent` is a local-first project for building a safer open source contribution workflow around AI.

Instead of blindly mass-opening pull requests, it helps you:

- inspect GitHub repositories before acting
- prioritize issues using issue text and comment signals
- draft scoped implementation plans
- prepare PR and maintainer-reply drafts in Markdown
- keep session and run logs for review
- walk through a four-step confirmation UI before any branch submission step

This repository is intentionally conservative. It does **not** auto-push code or auto-open pull requests yet. The current focus is reviewability, traceability, and human confirmation.

## Why It Exists

Autonomous bulk PR systems are technically possible, but they often fail for social and operational reasons:

- solving the wrong problem
- opening low-quality or unwanted PRs
- ignoring project contribution norms
- overwhelming maintainers
- triggering platform abuse controls

This project takes the opposite approach: inspect first, confirm scope, then draft.

## Features

- GitHub repository discovery through the public API
- repository scoring with conservative heuristics
- issue harvesting with fallback search strategies
- comment-aware prioritization for bugs and feature requests
- local bundle generation:
  - `summary.json`
  - `analysis.md`
  - `task.md`
  - `pr_draft.md`
  - `reply_draft.md`
- Markdown run logs and web session logs
- local web UI with a guided 4-step flow
- Markdown editing and preview for PRs and review replies
- multilingual interface support:
  - English
  - Simplified Chinese
  - Japanese
  - Korean
- day/night theme switching in the web UI

## Web Flow

The web workspace follows a clear review path:

1. Enter a GitHub repository URL and inspect stars plus major bug/feature discussions.
2. Confirm or edit the proposed solution outline.
3. Edit the PR body and maintainer reply in Markdown, then preview both.
4. Prepare a submission-branch artifact and leave it in a waiting-for-confirmation state.

## Quick Start

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Create a config file

```bash
cp examples/config.example.json config.json
```

Optional, but strongly recommended for rate limits:

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

### 3. Run the CLI

Discover repositories:

```bash
oss-pr-agent discover --config config.json
```

Generate local bundles:

```bash
oss-pr-agent draft --config config.json
```

### 4. Run the web UI

```bash
oss-pr-agent web --config config.json --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Example Commands

Inspect a narrow search slice:

```bash
oss-pr-agent discover --config config.json --limit 5
```

Generate bundles for accepted repositories:

```bash
oss-pr-agent draft --config config.json --limit 3
```

Use a one-off query:

```bash
oss-pr-agent discover --config config.json --query "topic:cli language:python stars:>150 pushed:>2025-01-01 archived:false"
```

Launch the local review console:

```bash
oss-pr-agent web --config config.json --host 127.0.0.1 --port 8000
```

## Configuration

Example `config.json`:

```json
{
  "query": "topic:python language:python stars:>200 archived:false",
  "limit": 10,
  "output_dir": "out",
  "log_dir": "out/logs",
  "min_score": 45,
  "issue_labels": ["good first issue", "help wanted"],
  "max_open_issues_per_repo": 5,
  "max_comments_per_issue": 10,
  "allow_missing_contributing": false,
  "require_recent_activity_days": 120
}
```

## Output

Bundle output includes:

- `summary.json`
- `analysis.md`
- `task.md`
- `pr_draft.md`
- `reply_draft.md`

Run and session logging includes:

- Markdown run logs under `out/logs/`
- Markdown session logs under `out/logs/`
- branch-preparation artifacts under `out/submissions/`

## Repository Layout

```text
.
|-- README.md
|-- README.zh-CN.md
|-- README.ja.md
|-- README.ko.md
|-- README.ru.md
|-- docs/
|   |-- ARCHITECTURE.md
|   `-- OPERATIONS.md
|-- examples/
|   `-- config.example.json
|-- pyproject.toml
`-- src/
    `-- oss_pr_agent/
```

## Documentation

- [Architecture](/Users/wangboyu/Documents/New project/docs/ARCHITECTURE.md)
- [Operations](/Users/wangboyu/Documents/New project/docs/OPERATIONS.md)

## Current Limitations

Not implemented yet:

- automatic code changes inside target repositories
- automatic branch push to GitHub
- automatic pull request creation
- webhook-driven maintainer reply automation
- sandboxed repository execution for code changes

## License And Publishing Notes

This local workspace started without a GitHub remote. Once your remote is ready, you can publish with:

```bash
git remote add origin <your-github-repo-url>
git push -u origin main
git push -u origin codex/github-pr-agent-mvp
```

