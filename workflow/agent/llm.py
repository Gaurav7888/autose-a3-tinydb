"""Anthropic Messages API client. The token never goes back into the environment."""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request

from models import TOKEN_CAP

_SECRET = re.compile(r"sk-ant-[A-Za-z0-9_\-]+")


class BudgetExceeded(RuntimeError):
    pass


class LLMError(RuntimeError):
    pass


class Reply:
    def __init__(self, text: str, content: list) -> None:
        self.text = text
        self.content = content

    def tool_uses(self) -> list[dict]:
        return [block for block in self.content if isinstance(block, dict) and block.get("type") == "tool_use"]


def scrub(text: str) -> str:
    return _SECRET.sub("[redacted]", text or "")


class Usage:
    def __init__(self) -> None:
        self.input_tokens = 0
        self.output_tokens = 0
        self.calls = 0

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens

    def add(self, payload: dict) -> None:
        usage = payload.get("usage") or {}
        self.input_tokens += int(usage.get("input_tokens") or 0)
        self.output_tokens += int(usage.get("output_tokens") or 0)
        self.calls += 1

    def as_dict(self) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "calls": self.calls,
        }


class LLM:
    def __init__(self) -> None:
        token = os.environ.pop("ANTHROPIC_AUTH_TOKEN", "") or os.environ.pop(
            "ANTHROPIC_API_KEY", ""
        )
        os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)
        os.environ.pop("ANTHROPIC_API_KEY", None)
        os.environ.pop("GH_TOKEN", None)
        os.environ.pop("GITHUB_TOKEN", None)
        if not token:
            raise LLMError("ANTHROPIC_AUTH_TOKEN is not set")
        self._token = token
        self._api_key = token.startswith("sk-ant-api")
        self.usage = Usage()

    def complete(self, model: str, system: str, messages: list[dict], max_tokens: int = 4096) -> str:
        return self.converse(model, system, messages, max_tokens=max_tokens).text

    def converse(self, model: str, system: str, messages: list[dict], tools: list | None = None, max_tokens: int = 4096) -> Reply:
        if self.usage.total > TOKEN_CAP:
            raise BudgetExceeded(f"token cap {TOKEN_CAP} exceeded")
        payload_in = {
            "model": model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
        }
        if tools:
            payload_in["tools"] = tools
        body = json.dumps(payload_in).encode()
        headers = {
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        if self._api_key:
            headers["x-api-key"] = self._token
        else:
            headers["authorization"] = f"Bearer {self._token}"
            headers["anthropic-beta"] = "oauth-2025-04-20"
        last_error = "no response"
        for attempt in range(4):
            request = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=body,
                headers=headers,
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=180) as response:
                    payload = json.loads(response.read().decode())
                break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")[:400]
                last_error = f"HTTP {exc.code}: {scrub(detail)}"
                if exc.code in (429, 529, 500, 502, 503) and attempt < 3:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise LLMError(last_error) from exc
            except urllib.error.URLError as exc:
                last_error = str(exc.reason)
                if attempt < 3:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise LLMError(last_error) from exc
        else:
            raise LLMError(last_error)
        self.usage.add(payload)
        if self.usage.total > TOKEN_CAP:
            raise BudgetExceeded(f"token cap {TOKEN_CAP} exceeded during the call")
        content = payload.get("content") or []
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text") or "")
        return Reply(scrub("".join(parts)), content)
