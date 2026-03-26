# Architecture

## Goal

Build a safe path from repository discovery to AI-assisted contribution without jumping straight to autonomous PR spam.

## MVP Flow

```text
GitHub Search API
        |
        v
Repository Discovery
        |
        v
Repository Evaluation
        |
        v
Issue Harvesting
        |
        v
Issue + Comment Analysis
        |
        v
Task Selection
        |
        v
Bundle Generation
        |
        v
Markdown Run Log
```

## Core Modules

### `github_api.py`

Thin wrapper around GitHub REST endpoints:

- search repositories
- fetch repository metadata
- search issues by label
- fetch issue comments
- check whether standard files exist

### `scoring.py`

Applies conservative heuristics:

- skip archived repositories
- reward active repositories
- reward projects with issues and contribution guidance
- penalize very low star count
- penalize stale repositories

### `planner.py`

Turns raw repository and issue data into:

- a selected opportunity
- a safe contribution thesis
- a PR draft structure
- a maintainer reply draft
- comment-aware prioritization between candidate issues

### `renderer.py`

Writes machine-readable and human-readable bundle artifacts to disk.

Also writes Markdown run logs for auditability.

### `workflow.py`

Orchestrates the pipeline:

- discover
- evaluate
- draft

### `service.py`

Adapts the repository analysis flow for single-repository inspection from the web UI.

### `webapp.py`

Runs a local review console with explicit confirmation gates between analysis, solution selection, draft editing, and branch preparation.

## Safety Model

The MVP is designed around three safety principles:

1. Do not mutate third-party repositories.
2. Do not contact maintainers automatically.
3. Do not hide uncertainty.

That is why outputs are drafts rather than live GitHub actions.

## Suggested Next Steps

If you want to move from MVP to a real agent system, add these layers in order:

1. Sandboxed repository checkout and test execution
2. LLM coding agent that edits only after a task is accepted
3. PR creation with per-repository rate limits
4. Comment reply agent with human approval for the first N runs
5. Feedback loop that learns from accepted and rejected PRs

## Recommended Production Controls

- per-day PR cap
- repository allowlist before public rollout
- explicit `CONTRIBUTING.md` and license checks
- issue-linked only mode
- human review for any feature request work
- automated opt-out list
