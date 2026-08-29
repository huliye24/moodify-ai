"""LalalClient unit tests via httpx.MockTransport (LALAL-STEMS-001)."""

from __future__ import annotations

import httpx
import pytest

from moodify.stems.client import LalalClient
from moodify.stems.errors import (
    StemLicenseInvalid,
    StemTaskUnknown,
    StemUpstreamError,
    StemUpstreamRejected,
)


def _client_with(handler) -> LalalClient:
    return LalalClient(
        license_key="test-key",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


class _Recorder:
    def __init__(self, response_factory):
        self.requests: list[httpx.Request] = []
        self.response_factory = response_factory

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.response_factory(request)


def test_upload_sends_file_with_headers_and_parses_source_id(tmp_path):
    seen = {}

    def factory(request):
        seen["url"] = str(request.url)
        seen["license"] = request.headers.get("X-License-Key")
        seen["disposition"] = request.headers.get("Content-Disposition")
        seen["body"] = request.content
        return httpx.Response(200, json={"id": "src_123"})

    rec = _Recorder(factory)
    client = _client_with(rec.handler)
    path = tmp_path / "input.wav"
    path.write_bytes(b"RIFFtest")

    source_id = client.upload(path, "input.wav")

    assert source_id == "src_123"
    assert seen["url"] == "https://www.lalal.ai/api/v1/upload/"
    assert seen["license"] == "test-key"
    assert seen["disposition"] == 'attachment; filename="input.wav"'
    assert seen["body"] == b"RIFFtest"


def test_upload_unicode_filename_uses_rfc5987(tmp_path):
    seen = {}

    def factory(request):
        seen["disposition"] = request.headers.get("Content-Disposition")
        return httpx.Response(200, json={"id": "s"})

    rec = _Recorder(factory)
    path = tmp_path / "歌.wav"
    path.write_bytes(b"x")
    _client_with(rec.handler).upload(path, "歌.wav")

    assert seen["disposition"].startswith("attachment; filename*=utf-8''")


def test_split_sends_presets_and_returns_task_id():
    seen = {}

    def factory(request):
        seen["url"] = str(request.url)
        seen["json"] = request.read().decode()
        return httpx.Response(200, json={"task_id": "task_9"})

    rec = _Recorder(factory)
    task_id = _client_with(rec.handler).split(
        "src_1",
        {"stem": "vocals", "extraction_level": "deep_extraction", "splitter": "auto"},
    )

    assert task_id == "task_9"
    assert seen["url"] == "https://www.lalal.ai/api/v1/split/stem_separator/"
    import json

    body = json.loads(seen["json"])
    assert body == {
        "source_id": "src_1",
        "presets": {"stem": "vocals", "extraction_level": "deep_extraction", "splitter": "auto"},
    }


def test_check_parses_progress_success_and_result_urls():
    def factory(request):
        body = request.read().decode()
        assert '"task_ids":["t1","t2"]' in body.replace(" ", "")
        return httpx.Response(
            200,
            json={
                "result": {
                    "t1": {"status": "progress", "progress": 40, "presets": {"stem": "vocals"}},
                    "t2": {
                        "status": "success",
                        "progress": 100,
                        "result": {
                            "tracks": [
                                {"type": "stem", "label": "vocals", "url": "https://cdn.lalal.ai/out1.wav"},
                                {"type": "back", "label": "no_vocals", "url": "https://cdn.lalal.ai/out1_back.wav"},
                            ],
                            "duration": 25,
                        },
                    },
                }
            },
        )

    rec = _Recorder(factory)
    result = _client_with(rec.handler).check(["t1", "t2"])

    assert result["t1"]["status"] == "progress"
    assert result["t1"]["progress"] == 40
    assert result["t2"]["status"] == "success"
    assert result["t2"]["result"]["tracks"][0]["url"] == "https://cdn.lalal.ai/out1.wav"
    assert result["t2"]["result"]["tracks"][1]["type"] == "back"


@pytest.mark.parametrize("status_code", [401, 403])
def test_upload_license_rejected(status_code, tmp_path):
    path = tmp_path / "a.wav"
    path.write_bytes(b"x")
    client = _client_with(lambda request: httpx.Response(status_code, text="no"))
    with pytest.raises(StemLicenseInvalid):
        client.upload(path, "a.wav")


def test_split_other_4xx_raises_upstream_rejected():
    client = _client_with(lambda request: httpx.Response(422, json={"detail": "bad stem"}))
    with pytest.raises(StemUpstreamRejected) as exc:
        client.split("s", {"stem": "banjo"})
    assert "bad stem" in exc.value.message


def test_check_5xx_raises_upstream_error():
    client = _client_with(lambda request: httpx.Response(500, text="boom"))
    with pytest.raises(StemUpstreamError):
        client.check(["t1"])


def test_check_transport_error_raises_upstream_error():
    def boom(request):
        raise httpx.ConnectError("no route to host")

    client = _client_with(boom)
    with pytest.raises(StemUpstreamError):
        client.check(["t1"])


def test_check_missing_task_raises_task_unknown():
    def factory(request):
        return httpx.Response(200, json={"result": {}})

    client = _client_with(factory)
    with pytest.raises(StemTaskUnknown):
        client.check(["missing"])
