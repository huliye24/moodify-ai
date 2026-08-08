from moodify.lyric_align.pipeline import canonical_sha256, file_sha256


def test_canonical_sha256_is_key_order_independent() -> None:
    first = canonical_sha256({"b": 2, "a": 1})
    second = canonical_sha256({"a": 1, "b": 2})
    assert first == second


def test_canonical_sha256_differs_on_value_change() -> None:
    assert canonical_sha256({"a": 1}) != canonical_sha256({"a": 2})


def test_canonical_sha256_is_unicode_stable() -> None:
    payload = {"text": "J'écris encore, très doucement. 中文歌词"}
    assert canonical_sha256(payload) == canonical_sha256({"text": "J'écris encore, très doucement. 中文歌词"})


def test_file_sha256_is_stable(tmp_path) -> None:
    target = tmp_path / "sample.txt"
    target.write_text("contenu", encoding="utf-8")
    assert file_sha256(target) == file_sha256(target)
