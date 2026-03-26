from __future__ import annotations

import html
import re


def render_markdown(text: str) -> str:
    lines = text.replace("\r\n", "\n").split("\n")
    blocks = []
    in_list = False
    in_code = False
    code_lines = []
    paragraph = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            content = " ".join(paragraph).strip()
            blocks.append(f"<p>{_inline(content)}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal in_list
        if in_list:
            blocks.append("</ul>")
            in_list = False

    def flush_code() -> None:
        nonlocal in_code, code_lines
        if in_code:
            escaped = html.escape("\n".join(code_lines))
            blocks.append(f"<pre><code>{escaped}</code></pre>")
            in_code = False
            code_lines = []

    for raw_line in lines:
        line = raw_line.rstrip()
        if line.startswith("```"):
            flush_paragraph()
            flush_list()
            if in_code:
                flush_code()
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(raw_line)
            continue
        if not line.strip():
            flush_paragraph()
            flush_list()
            continue
        if line.startswith("#"):
            flush_paragraph()
            flush_list()
            level = min(len(line) - len(line.lstrip("#")), 6)
            content = line[level:].strip()
            blocks.append(f"<h{level}>{_inline(content)}</h{level}>")
            continue
        if line.startswith("- "):
            flush_paragraph()
            if not in_list:
                blocks.append("<ul>")
                in_list = True
            blocks.append(f"<li>{_inline(line[2:].strip())}</li>")
            continue
        paragraph.append(line.strip())

    flush_paragraph()
    flush_list()
    flush_code()
    return "\n".join(blocks)


def _inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noreferrer">\1</a>', escaped)
    return escaped
