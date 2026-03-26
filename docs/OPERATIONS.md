# Operations Guide

## Running the MVP

### Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Configure

Create `config.json` from the example file and tune:

- `query`: GitHub search query
- `limit`: max repositories to inspect
- `min_score`: minimum repo score to keep
- `issue_labels`: preferred labels for candidate tasks
- `require_recent_activity_days`: freshness threshold
- `max_comments_per_issue`: number of recent comments to inspect per issue
- `log_dir`: where Markdown run logs should be written

### Execute

```bash
oss-pr-agent discover --config config.json
oss-pr-agent draft --config config.json
oss-pr-agent web --config config.json --host 127.0.0.1 --port 8000
```

After `draft`, review:

- repository bundles under `out/`
- Markdown logs under `out/logs/`

For the web flow, also review:

- session logs under `out/logs/`
- prepared submission artifacts under `out/submissions/`

## Rate Limits

Without `GITHUB_TOKEN`, GitHub's unauthenticated rate limit is low. Use a token for any real scanning session.

## Risk Notes

Do not enable automatic PR creation until you have:

- an allowlist of repositories
- branch protection awareness
- a robust test execution sandbox
- abuse prevention controls
- a real review policy

## Suggested Rollout

1. Run the current MVP on a narrow topic, such as `topic:cli language:python`.
2. Review the generated bundles manually.
3. Read the Markdown run log to confirm the selected issue matches the discussion context.
4. Pick one repository and one issue.
5. Clone it into a sandbox and let a coding agent prepare a patch.
6. Only after repeated success should you automate PR creation.
