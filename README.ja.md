# OSS PR Agent

<p align="center">
  <strong>OSS の課題発見、解決方針の整理、PR ドラフト作成、ログ管理を行うローカルファーストの AI ワークスペース。</strong>
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="./README.zh-CN.md">简体中文</a> ·
  <a href="./README.ja.md">日本語</a> ·
  <a href="./README.ko.md">한국어</a> ·
  <a href="./README.ru.md">Русский</a>
</p>

## 概要

`OSS PR Agent` は、AI を使ったオープンソース貢献フローを、より安全で確認しやすい形にするためのローカルファーストなプロジェクトです。

現在できること:

- GitHub リポジトリの調査と評価
- issue 本文とコメントを使ったバグ・要望の優先順位付け
- 実装方針のドラフト作成
- PR 本文とメンテナー返信の Markdown 下書き作成
- 実行ログとセッションログの保存
- 4 段階の Web UI による確認フロー

## この設計にした理由

大量の自動 PR は技術的には可能ですが、実際の失敗要因は次のようなものです。

- 問題設定がずれている
- PR の品質が安定しない
- プロジェクト固有の運用を無視してしまう
- メンテナーへの負担になる
- プラットフォームの abuse 制御に触れる

そのため、このプロジェクトは「分析 -> 確認 -> 下書き」を先に重視しています。

## 主な機能

- GitHub リポジトリ探索
- 保守的なリポジトリ評価ルール
- issue 収集とフォールバック検索
- コメントを使ったバグ/要望の優先付け
- ローカル bundle 生成:
  - `summary.json`
  - `analysis.md`
  - `task.md`
  - `pr_draft.md`
  - `reply_draft.md`
- Markdown ログ
- 4 ステップの Web ワークスペース
- PR と返信の Markdown 編集・プレビュー
- 多言語 UI:
  - English
  - 简体中文
  - 日本語
  - 한국어
- 昼 / 夜テーマ切り替え

## Web フロー

1. GitHub リポジトリ URL を入力し、star 数と主要な議論を確認
2. 解決方針を確認または編集
3. PR と返信を Markdown で編集し、プレビュー
4. 確認待ちのブランチ準備情報を生成

## クイックスタート

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp examples/config.example.json config.json
export GITHUB_TOKEN=ghp_your_token_here
```

CLI:

```bash
oss-pr-agent discover --config config.json
oss-pr-agent draft --config config.json
```

Web UI:

```bash
oss-pr-agent web --config config.json --host 127.0.0.1 --port 8000
```

## 設定例

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

## 出力

- bundle ファイル
- `out/logs/` の実行ログとセッションログ
- `out/submissions/` の提出準備ファイル

## ドキュメント

- [Architecture](/Users/wangboyu/Documents/New project/docs/ARCHITECTURE.md)
- [Operations](/Users/wangboyu/Documents/New project/docs/OPERATIONS.md)

## 未実装の項目

- 対象リポジトリへの自動コード変更
- GitHub への自動 push
- 自動 PR 作成
- webhook ベースの自動返信
- サンドボックス実行

