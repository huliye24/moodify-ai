"""lalal.ai API V1 client (LALAL-STEMS-001).

Thin synchronous wrapper over upload / split / check. No automatic retry
of /split/ — a submitted split is billed, so retries could double-charge.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

import httpx

from .constants import DEFAULT_BASE_URL
from .errors import (
    StemLicenseInvalid,
    StemTaskUnknown,
    StemUpstreamError,
    StemUpstreamRejected,
)

UPLOAD_TIMEOUT = 120.0
DEFAULT_TIMEOUT = 60.0


def _content_disposition(filename: str) -> str:
    try:
        filename.encode("ascii")
        return f'attachment; filename="{filename}"'
    except UnicodeEncodeError:
        return f"attachment; filename*=utf-8''{quote(filename)}"


class LalalClient:
    def __init__(
        self,
        license_key: str,
        base_url: str = DEFAULT_BASE_URL,
        client: httpx.Client | None = None,
    ) -> None:
        self.license_key = license_key
        self.base_url = base_url.rstrip("/") + "/"
        # Injected client (httpx.MockTransport in tests); otherwise a fresh one.
        self._client = client or httpx.Client(timeout=DEFAULT_TIMEOUT)

    def _headers(self) -> dict[str, str]:
        return {"X-License-Key": self.license_key}

    def upload(self, path: Path, filename: str) -> str:
        """Upload a local audio file and return the lalal source_id."""
        headers = {"Content-Disposition": _content_disposition(filename), **self._headers()}
        try:
            with path.open("rb") as handle:
                response = self._client.post(
                    self.base_url + "upload/",
                    content=handle,
                    headers=headers,
                    timeout=UPLOAD_TIMEOUT,
                )
        except httpx.HTTPError as exc:
            raise StemUpstreamError(f"upload transport failure: {exc}") from exc
        self._raise_for_status(response, "upload")
        return response.json()["id"]

    def split(self, source_id: str, presets: dict) -> str:
        """Submit one stem separation task and return the lalal task_id."""
        body = {"source_id": source_id, "presets": presets}
        try:
            response = self._client.post(
                self.base_url + "split/stem_separator/",
                json=body,
                headers=self._headers(),
            )
        except httpx.HTTPError as exc:
            raise StemUpstreamError(f"split transport failure: {exc}") from exc
        self._raise_for_status(response, "split")
        return response.json()["task_id"]

    def check(self, task_ids: list[str]) -> dict:
        """Query task statuses; returns the parsed {task_id: status} map."""
        body = {"task_ids": list(task_ids)}
        try:
            response = self._client.post(
                self.base_url + "check/",
                json=body,
                headers=self._headers(),
            )
        except httpx.HTTPError as exc:
            raise StemUpstreamError(f"check transport failure: {exc}") from exc
        self._raise_for_status(response, "check")
        result = response.json().get("result", {})
        for task_id in task_ids:
            if task_id not in result:
                raise StemTaskUnknown(f"task {task_id} unknown to lalal.ai")
        return result

    def _raise_for_status(self, response: httpx.Response, operation: str) -> None:
        if response.status_code in (401, 403):
            raise StemLicenseInvalid(f"lalal.ai rejected license key ({operation})")
        if response.status_code >= 500:
            raise StemUpstreamError(
                f"lalal.ai {operation} failed: {response.status_code}"
            )
        if response.status_code >= 400:
            detail = _extract_detail(response)
            raise StemUpstreamRejected(
                f"lalal.ai rejected {operation}: {response.status_code} {detail}"
            )


def _extract_detail(response: httpx.Response) -> str:
    try:
        payload = json.loads(response.text)
        if isinstance(payload, dict) and "detail" in payload:
            return str(payload["detail"])[:500]
    except (ValueError, TypeError):
        pass
    return response.text[:500]
