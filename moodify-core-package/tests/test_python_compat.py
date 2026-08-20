from moodify.compat import StrEnum


class Example(StrEnum):
    VALUE = "VALUE"


def test_str_enum_serializes_as_string_value():
    assert str(Example.VALUE) == "VALUE"
    assert Example.VALUE == "VALUE"
