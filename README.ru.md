# OSS PR Agent

<p align="center">
  <strong>Локальный AI‑workspace для поиска задач в OSS, подготовки решений, черновиков PR и прозрачных журналов работы.</strong>
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="./README.zh-CN.md">简体中文</a> ·
  <a href="./README.ja.md">日本語</a> ·
  <a href="./README.ko.md">한국어</a> ·
  <a href="./README.ru.md">Русский</a>
</p>

## Обзор

`OSS PR Agent` — это локальный проект для более безопасного AI‑процесса участия в open source.

Сейчас он помогает:

- анализировать GitHub-репозитории до любых действий
- находить баги и feature request'ы по issue и комментариям
- готовить аккуратный план решения
- создавать Markdown-черновики для PR и ответов мейнтейнерам
- сохранять run log и session log
- проходить через 4-шаговый web-интерфейс подтверждения

## Зачем такой подход

Массовая автоматическая отправка PR технически возможна, но на практике часто приводит к проблемам:

- решается не та задача
- PR низкого качества
- игнорируются правила проекта
- создается шум для мейнтейнеров
- срабатывают anti-abuse ограничения платформы

Поэтому здесь приоритет такой: `анализ -> подтверждение -> черновик`.

## Возможности

- поиск репозиториев через GitHub API
- консервативная оценка репозиториев
- сбор issue с fallback-стратегиями
- приоритизация багов и feature request'ов по комментариям
- локальная генерация bundle-файлов:
  - `summary.json`
  - `analysis.md`
  - `task.md`
  - `pr_draft.md`
  - `reply_draft.md`
- Markdown-журналы
- локальный web UI с 4 шагами
- редактирование и preview Markdown для PR и reply
- многоязычный интерфейс:
  - English
  - 简体中文
  - 日本語
  - 한국어
- переключение day / night темы

## Web Flow

1. Ввести URL GitHub-репозитория
2. Подтвердить или изменить предложенное решение
3. Отредактировать PR и reply в Markdown и посмотреть preview
4. Подготовить артефакт ветки в состоянии ожидания подтверждения

## Быстрый старт

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

## Пример конфигурации

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

## Выходные данные

- bundle-файлы
- журналы в `out/logs/`
- артефакты подготовки отправки в `out/submissions/`

## Документация

- [Architecture](/Users/wangboyu/Documents/New project/docs/ARCHITECTURE.md)
- [Operations](/Users/wangboyu/Documents/New project/docs/OPERATIONS.md)

## Пока не реализовано

- автоматическое изменение кода в целевых репозиториях
- автоматический push веток в GitHub
- автоматическое создание PR
- автоматические ответы по webhook
- sandbox-выполнение для реальных кодовых изменений

