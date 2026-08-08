from moodify.lyric_align.lyrics import clean_lyrics, normalize_for_alignment, split_words


def test_clean_removes_structure_labels() -> None:
    raw = """[Couplet 1]\nJe veux vieillir avec toi\n\nRefrain\nAvec toi\n[Outro]\n"""
    assert clean_lyrics(raw) == ["Je veux vieillir avec toi", "Avec toi"]


def test_french_normalization_preserves_display_separately() -> None:
    assert normalize_for_alignment("J'écris encore, très doucement.", "fr") == "j'ecris encore tres doucement"


def test_chinese_character_split() -> None:
    assert split_words("我想与你一起老去。", "zh") == list("我想与你一起老去")


def test_french_hyphenated_words_kept() -> None:
    assert normalize_for_alignment("C'est un rendez-vous à minuit.", "fr") == "c'est un rendez-vous a minuit"


def test_french_elision_kept() -> None:
    assert normalize_for_alignment("J'aime l'océan et l'âme.", "fr") == "j'aime l'ocean et l'ame"


def test_french_punctuation_removed_without_losing_display_text() -> None:
    display = "Lève-toi, mon amour !"
    normalized = normalize_for_alignment(display, "fr")
    assert normalized == "leve-toi mon amour"
    assert "é" not in normalized


def test_chinese_display_characters_unchanged() -> None:
    display = "夜色温柔，星光闪烁。"
    normalized = normalize_for_alignment(display, "zh")
    assert "夜" in normalized and "色" in normalized and "光" in normalized
    assert normalized == "夜色温柔 星光闪烁"
