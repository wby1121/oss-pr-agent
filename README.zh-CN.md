# OSS PR Agent

<p align="center">
  <strong>一个本地优先的 AI 开源协作工作台，用来发现问题、规划改动、起草 PR，并保留完整日志。</strong>
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="./README.zh-CN.md">简体中文</a> ·
  <a href="./README.ja.md">日本語</a> ·
  <a href="./README.ko.md">한국어</a> ·
  <a href="./README.ru.md">Русский</a>
</p>

## 简介

`OSS PR Agent` 是一个围绕 AI 构建的开源贡献工作流项目，但它默认走“先分析、再确认、最后起草”的保守路径，而不是一上来就批量自动发 PR。

它目前可以帮助你：

- 扫描和评估 GitHub 仓库
- 结合 issue 正文和评论信号来优先发现 bug 与需求
- 生成可审阅的解决方案与 PR 草稿
- 生成维护者评论回复草稿
- 记录运行日志与会话日志
- 通过 4 步 Web 界面逐步确认操作

## 为什么这样设计

大规模自动开 PR 在技术上可行，但常见问题通常不是“代码写不出来”，而是：

- 解决错了问题
- PR 质量不稳定
- 忽略项目的贡献规范
- 打扰维护者
- 触发平台风控

所以这个项目优先强调：

- 可审阅
- 可追踪
- 可确认

## 功能特性

- GitHub 仓库发现与筛选
- 保守的仓库评分规则
- issue 抓取与回退搜索
- 基于评论语义的 bug / 需求优先级
- 本地 bundle 产物生成：
  - `summary.json`
  - `analysis.md`
  - `task.md`
  - `pr_draft.md`
  - `reply_draft.md`
- Markdown 日志与会话记录
- 4 步式本地 Web 工作台
- PR 与评论回复的 Markdown 编辑与预览
- 多语言界面：
  - 中文
  - 英文
  - 日文
  - 韩文
- 日间 / 夜间主题切换

## Web 流程

1. 输入 GitHub 仓库地址，查看 star、主要 bug 和需求讨论。
2. 确认或修改推荐解决方案。
3. 编辑 PR 与评论回复，并进行 Markdown 预览。
4. 生成待确认分支提交信息。

## 快速开始

### 1. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. 创建配置文件

```bash
cp examples/config.example.json config.json
```

推荐配置 GitHub Token 以提升 API 额度：

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

### 3. 使用 CLI

扫描仓库：

```bash
oss-pr-agent discover --config config.json
```

生成 bundle：

```bash
oss-pr-agent draft --config config.json
```

### 4. 启动 Web 界面

```bash
oss-pr-agent web --config config.json --host 127.0.0.1 --port 8000
```

打开 [http://127.0.0.1:8000](http://127.0.0.1:8000)。

## 示例命令

```bash
oss-pr-agent discover --config config.json --limit 5
oss-pr-agent draft --config config.json --limit 3
oss-pr-agent web --config config.json --host 127.0.0.1 --port 8000
```

## 配置示例

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

## 输出内容

主要输出包括：

- `summary.json`
- `analysis.md`
- `task.md`
- `pr_draft.md`
- `reply_draft.md`
- `out/logs/` 下的运行日志与会话日志
- `out/submissions/` 下的待确认提交文件

## 文档

- [架构说明](/Users/wangboyu/Documents/New project/docs/ARCHITECTURE.md)
- [运行说明](/Users/wangboyu/Documents/New project/docs/OPERATIONS.md)

## 当前限制

目前还没有实现：

- 自动修改目标仓库代码
- 自动推送远端分支
- 自动创建 PR
- 基于 webhook 的自动回复
- 针对目标仓库的安全沙箱执行

