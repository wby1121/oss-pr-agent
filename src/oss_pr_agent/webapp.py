from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Tuple

from .config import AppConfig
from .github_api import GitHubClient
from .markdown import render_markdown
from .renderer import slugify, write_session_log
from .service import RepoInspector


class SessionStore:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._sessions: Dict[str, Dict] = {}

    def create(self, inspection: Dict) -> Dict:
        session_id = uuid.uuid4().hex[:10]
        recommended = inspection.get("recommended")
        session = {
            "id": session_id,
            "status": "analyzed",
            "repo": inspection["repo"],
            "scorecard": inspection["scorecard"],
            "candidates": inspection["candidates"],
            "recommended": recommended,
            "solution": recommended,
            "drafts": {},
            "submission": None,
            "log_path": "",
        }
        session["log_path"] = str(write_session_log(self.config.log_dir, session))
        self._sessions[session_id] = session
        return session

    def get(self, session_id: str) -> Dict:
        if session_id not in self._sessions:
            raise KeyError(session_id)
        return self._sessions[session_id]

    def update(self, session_id: str, **changes: Dict) -> Dict:
        session = self.get(session_id)
        session.update(changes)
        session["log_path"] = str(write_session_log(self.config.log_dir, session))
        return session


def _json_response(handler: BaseHTTPRequestHandler, payload: Dict, status: int = 200) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _parse_body(handler: BaseHTTPRequestHandler) -> Dict:
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length) if length else b"{}"
    return json.loads(raw.decode("utf-8"))


def _load_static_asset(name: str) -> Tuple[bytes, str]:
    asset_path = Path(__file__).parent / "web_static" / name
    suffix_map = {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
    }
    return asset_path.read_bytes(), suffix_map[asset_path.suffix]


def build_handler(config: AppConfig):
    inspector = RepoInspector(config=config, client=GitHubClient())
    sessions = SessionStore(config=config)

    class AppHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self._serve_static(send_body=True)

        def do_HEAD(self) -> None:
            self._serve_static(send_body=False)

        def _serve_static(self, send_body: bool) -> None:
            if self.path in {"/", "/index.html"}:
                body, content_type = _load_static_asset("index.html")
                self._write_bytes(body, content_type, send_body=send_body)
                return
            if self.path == "/app.js":
                body, content_type = _load_static_asset("app.js")
                self._write_bytes(body, content_type, send_body=send_body)
                return
            if self.path == "/styles.css":
                body, content_type = _load_static_asset("styles.css")
                self._write_bytes(body, content_type, send_body=send_body)
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def do_POST(self) -> None:
            try:
                if self.path == "/api/analyze":
                    payload = _parse_body(self)
                    result = inspector.inspect_repository(payload["repo_url"])
                    session = sessions.create(RepoInspector.serialize(result))
                    _json_response(self, {"session": _serialize_session(session)})
                    return
                if self.path == "/api/confirm-solution":
                    payload = _parse_body(self)
                    session = sessions.get(payload["session_id"])
                    source = session.get("recommended") or {}
                    edited_outline = payload.get("implementation_outline") or source.get("implementation_outline", [])
                    solution = {
                        **source,
                        "implementation_outline": edited_outline,
                        "priority_reason": payload.get("priority_reason", source.get("priority_reason", "")),
                    }
                    session = sessions.update(payload["session_id"], status="solution_confirmed", solution=solution)
                    drafts = {
                        "pr_title": source.get("pr_title", ""),
                        "pr_body": source.get("pr_body", ""),
                        "reply_body": source.get("reply_draft", ""),
                    }
                    session = sessions.update(payload["session_id"], drafts=drafts)
                    _json_response(self, {"session": _serialize_session(session)})
                    return
                if self.path == "/api/update-drafts":
                    payload = _parse_body(self)
                    session = sessions.update(
                        payload["session_id"],
                        status="drafts_ready",
                        drafts={
                            "pr_title": payload["pr_title"],
                            "pr_body": payload["pr_body"],
                            "reply_body": payload["reply_body"],
                        },
                    )
                    _json_response(
                        self,
                        {
                            "session": _serialize_session(session),
                            "preview": {
                                "pr_body_html": render_markdown(payload["pr_body"]),
                                "reply_body_html": render_markdown(payload["reply_body"]),
                            },
                        },
                    )
                    return
                if self.path == "/api/submit-branch":
                    payload = _parse_body(self)
                    session = sessions.get(payload["session_id"])
                    repo_slug = slugify(session["repo"]["full_name"])
                    issue_number = session["solution"]["issue_number"] if session.get("solution") else "draft"
                    branch_name = f"codex/{repo_slug}-issue-{issue_number}"
                    submission_dir = Path(config.output_dir) / "submissions"
                    submission_dir.mkdir(parents=True, exist_ok=True)
                    submission_path = submission_dir / f"{session['id']}.json"
                    submission_payload = {
                        "branch_name": branch_name,
                        "state": "waiting_for_confirmation",
                        "repo_url": session["repo"]["html_url"],
                        "pr_title": session["drafts"].get("pr_title", ""),
                    }
                    submission_path.write_text(json.dumps(submission_payload, indent=2), encoding="utf-8")
                    session = sessions.update(
                        payload["session_id"],
                        status="branch_prepared",
                        submission={
                            "branch_name": branch_name,
                            "state": "waiting_for_confirmation",
                            "path": str(submission_path),
                        },
                    )
                    _json_response(self, {"session": _serialize_session(session)})
                    return
            except KeyError:
                _json_response(self, {"error": "Session not found."}, status=404)
                return
            except Exception as exc:
                _json_response(self, {"error": str(exc)}, status=400)
                return

            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def log_message(self, format: str, *args) -> None:
            return

        def _write_bytes(self, body: bytes, content_type: str, send_body: bool) -> None:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if send_body:
                self.wfile.write(body)

    return AppHandler


def _serialize_session(session: Dict) -> Dict:
    return {
        "id": session["id"],
        "status": session["status"],
        "repo": session["repo"],
        "scorecard": session["scorecard"],
        "candidates": session["candidates"],
        "recommended": session["recommended"],
        "solution": session["solution"],
        "drafts": session["drafts"],
        "submission": session["submission"],
        "log_path": session["log_path"],
    }


def run_server(config: AppConfig, host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), build_handler(config))
    print(f"Serving OSS PR Agent UI at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
