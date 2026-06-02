"""Regression tests for safe subprocess argument passing.

These tests ensure that filenames with spaces, parentheses, quotes,
and CJK characters are correctly preserved as single arguments
during template → argv conversion.
"""

from moodify_runtime.utils import render_template_to_argv, quote_cmd

TEMPLATE = "{python} -m moodify.cli process {input} --preset {preset} --output-dir {output_dir}"

BASE_CONTEXT = {
    "python": "python3",
    "output_dir": "/tmp/test_output",
    "preset": "warm_vocal",
}

# ── filenames that MUST survive shlex round-trip ──────────────────────────

PROBLEMATIC_FILENAMES = [
    # spaces
    "_Black Therapy (1).mp3",
    "_Black Therapy (2).mp3",
    "_Black Therapy.mp3",
    "Control Theory.mp3",
    "Moonlight Girl.mp3",
    "_Neural Poison  .mp3",           # double space
    "_Neural Poison   - 副本.mp3",    # double space + CJK
    "Okay Okay 刚刚好.mp3",           # space + CJK
    "Silk and Ruin2.mp3",
    # parentheses + spaces
    "句点15 (1).mp3",
    "句点8 (1).mp3",
    "我想被偏爱，不想被路过 (1).mp3",
    "我曾遥望银河星光 (1).mp3",
    "散焦之界 (1).mp3",
    "茧中微光 (1).mp3",
    # single quotes (shell poison)
    "Raphael's Test.mp3",
    "Don't Stop Me Now.mp3",
    # pure CJK / special chars
    "北极星与黑夜_02.flac",
    "句点10.mp3",
    "唯有痛苦从不说谎.mp3",
    "多变的天气.mp3",
    "时间不对.mp3",
    # underscores and brackets
    "_Black Therapy.mp3",
    # mixed: quotes + spaces + parentheses
    "It's My Life (Live).mp3",
]


def _make_context(filename: str):
    ctx = dict(BASE_CONTEXT)
    ctx["input"] = f"/fake/path/{filename}"
    return ctx


def test_all_filenames_survive_round_trip():
    """Every filename must appear as exactly one argv element after 'process'."""
    for name in PROBLEMATIC_FILENAMES:
        ctx = _make_context(name)
        argv = render_template_to_argv(TEMPLATE, ctx)
        try:
            input_idx = argv.index("process") + 1
        except ValueError:
            raise AssertionError(f"'process' not found in argv for {name}")

        actual = argv[input_idx]
        assert actual == ctx["input"], (
            f"FILENAME SPLIT:\n"
            f"  input:    {ctx['input']}\n"
            f"  got arg:  {actual}\n"
            f"  full argv: {argv}"
        )


def test_no_unrecognized_arguments_pattern():
    """The displayed command should quote filenames with spaces/special chars."""
    for name in ["_Black Therapy (1).mp3", "Raphael's Test.mp3", "句点15 (1).mp3"]:
        ctx = _make_context(name)
        argv = render_template_to_argv(TEMPLATE, ctx)
        cmd_str = quote_cmd(argv)

        # The command string must contain quotes around the path
        # (shlex.quote adds single quotes when needed)
        assert "'" in cmd_str or '"' in cmd_str, (
            f"Path not quoted in display for {name}: {cmd_str}"
        )

        # The path itself should appear after shlex un-quoting inside argv
        input_idx = argv.index("process") + 1
        assert argv[input_idx] == ctx["input"]


def test_simple_filenames_still_work():
    """Filenames without special chars should work unchanged."""
    for name in ["假装无所谓2.mp3", "electronic.wav", "piano.wav", "echoes-in-the-neon-labyrinth.mp3"]:
        ctx = _make_context(name)
        argv = render_template_to_argv(TEMPLATE, ctx)
        input_idx = argv.index("process") + 1
        assert argv[input_idx] == ctx["input"]


def test_empty_and_edge_cases():
    """Edge cases should not crash."""
    ctx = dict(BASE_CONTEXT)
    ctx["input"] = ""
    argv = render_template_to_argv(TEMPLATE, ctx)
    # empty string should result in an empty-quoted argument
    input_idx = argv.index("process") + 1
    assert argv[input_idx] == ""

    # Very long filename
    long_name = "a" * 200 + " " + "b" * 200 + ".mp3"
    ctx["input"] = f"/tmp/{long_name}"
    argv = render_template_to_argv(TEMPLATE, ctx)
    input_idx = argv.index("process") + 1
    assert argv[input_idx] == ctx["input"]
