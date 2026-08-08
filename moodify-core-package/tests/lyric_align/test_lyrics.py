from moodify.lyric_align.lyrics import clean_lyrics, normalize_for_alignment, split_words


def test_clean_removes_structure_labels() -> None:
    raw = """[Couplet 1]\nJe veux vieillir avec toi\n\nRefrain\nAvec toi\n[Outro]\n"""
    assert clean_lyrics(raw) == ["Je veux vieillir avec toi", "Avec toi"]


def test_french_normalization_preserves_display_separately() -> None:
    assert normalize_for_alignment("J'écris encore, très doucement.", "fr") == "j'ecris encore tres doucement"


def test_chinese_character_split() -> None:
    assert split_words("我想与你一起老去。", "zh") == list("我想与你一起老去")
