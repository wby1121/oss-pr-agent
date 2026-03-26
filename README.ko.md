# OSS PR Agent

<p align="center">
  <strong>오픈소스 이슈 탐색, 해결안 정리, PR 초안 작성, 로그 추적을 위한 로컬 우선 AI 작업공간.</strong>
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="./README.zh-CN.md">简体中文</a> ·
  <a href="./README.ja.md">日本語</a> ·
  <a href="./README.ko.md">한국어</a> ·
  <a href="./README.ru.md">Русский</a>
</p>

## 소개

`OSS PR Agent` 는 AI 기반 오픈소스 기여 흐름을 더 안전하고 검토 가능한 형태로 만들기 위한 로컬 우선 프로젝트입니다.

현재 지원하는 기능:

- GitHub 저장소 탐색 및 평가
- issue 본문과 댓글을 활용한 버그/요구사항 우선순위 지정
- 구현 방향 초안 생성
- PR 본문 및 유지보수자 답변 Markdown 초안 작성
- 실행 로그와 세션 로그 기록
- 4단계 Web UI 확인 흐름

## 왜 이렇게 설계했는가

대량 자동 PR은 기술적으로 가능하지만, 실제 문제는 주로 다음과 같습니다.

- 잘못된 문제 해결
- 불안정한 PR 품질
- 프로젝트 관례 무시
- 유지보수자 부담 증가
- 플랫폼 abuse 제어 트리거

그래서 이 프로젝트는 자동 제출보다 `분석 -> 확인 -> 초안` 을 먼저 강조합니다.

## 주요 기능

- GitHub 저장소 검색
- 보수적인 저장소 점수화
- issue 수집 및 fallback 검색
- 댓글 기반 bug / feature 우선순위 판단
- 로컬 bundle 생성:
  - `summary.json`
  - `analysis.md`
  - `task.md`
  - `pr_draft.md`
  - `reply_draft.md`
- Markdown 로그
- 4단계 Web 작업공간
- PR / 답변 Markdown 편집 및 미리보기
- 다국어 UI:
  - English
  - 简体中文
  - 日本語
  - 한국어
- 주간 / 야간 테마 전환

## Web 흐름

1. GitHub 저장소 URL 입력
2. 해결안 확인 또는 수정
3. PR 및 댓글 답변 편집과 미리보기
4. 확인 대기 상태의 브랜치 준비 정보 생성

## 빠른 시작

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

## 설정 예시

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

## 출력

- bundle 파일
- `out/logs/` 의 실행/세션 로그
- `out/submissions/` 의 제출 준비 파일

## 문서

- [Architecture](/Users/wangboyu/Documents/New project/docs/ARCHITECTURE.md)
- [Operations](/Users/wangboyu/Documents/New project/docs/OPERATIONS.md)

## 아직 없는 기능

- 대상 저장소 자동 코드 수정
- GitHub 자동 push
- 자동 PR 생성
- webhook 기반 자동 답변
- 샌드박스 실행

