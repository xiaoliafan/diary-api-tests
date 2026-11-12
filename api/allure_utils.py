"""Allure 请求和响应附件工具。"""

import json
from typing import Any

import allure
import requests

_SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "proxy-authorization",
    "set-cookie",
}
_MAX_BODY_LENGTH = 10_000


def _safe_headers(headers: Any) -> dict[str, str]:
    return {
        key: "***" if key.lower() in _SENSITIVE_HEADERS else value
        for key, value in dict(headers).items()
    }


def _body_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    text = str(value)
    if len(text) > _MAX_BODY_LENGTH:
        return f"{text[:_MAX_BODY_LENGTH]}\n...<truncated>"
    return text


def _json_or_text(value: str) -> Any:
    if not value:
        return None
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return value


def attach_response(response: requests.Response, name: str | None = None) -> None:
    """把请求和响应写入 Allure 附件，敏感请求头会被脱敏。"""
    request = response.request
    payload = {
        "request": {
            "method": request.method,
            "url": request.url,
            "headers": _safe_headers(request.headers),
            "body": _json_or_text(_body_text(request.body)),
        },
        "response": {
            "status_code": response.status_code,
            "headers": _safe_headers(response.headers),
            "body": _json_or_text(_body_text(response.text)),
            "elapsed_ms": round(response.elapsed.total_seconds() * 1000, 2),
        },
    }
    allure.attach(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        name=name or f"{request.method} {request.url}",
        attachment_type=allure.attachment_type.JSON,
    )
