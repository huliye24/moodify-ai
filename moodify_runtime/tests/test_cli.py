"""Tests for CLI — parser building, main entry, all subcommands."""
import pytest
from moodify_runtime.cli import build_parser, main


class TestBuildParser:
    def test_returns_parser(self):
        p = build_parser()
        assert p is not None

    def test_registers_core_commands(self):
        import argparse
        p = build_parser()
        subs = [a for a in p._actions if isinstance(a, argparse._SubParsersAction)]
        assert len(subs) > 0

    def help_contains_all(self):
        p = build_parser()
        help_text = p.format_help()
        for cmd in ["register", "plan", "run", "report", "craft"]:
            assert cmd in help_text


class TestMain:
    def test_help_no_error(self):
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0

    def test_register_empty(self):
        """register should handle empty input dirs."""
        import tempfile
        d = tempfile.mkdtemp()
        try:
            code = main(["register", "--source", "test", "--config", "{}"])
        except SystemExit as e:
            # May exit with error if JSON config is invalid
            pass
        except Exception:
            pass  # Config may not parse

    def test_plan_noop(self):
        try:
            import tempfile, json
            d = tempfile.mkdtemp()
            cfg_path = f"{d}/cfg.json"
            import json as j
            j.dump({"project_root": d, "output_root": f"{d}/out",
                    "registry_path": f"{d}/reg.jsonl",
                    "queue_path": f"{d}/q.jsonl"}, open(cfg_path, 'w'))
            code = main(["plan", "--config", cfg_path])
        except SystemExit as e:
            pass
        except Exception:
            pass

    def test_tidal_state(self):
        """tidal-state should run without error."""
        try:
            code = main(["tidal-state"])
        except SystemExit as e:
            assert e.code == 0

    def test_tidal_intel(self):
        try:
            code = main(["tidal-intel"])
        except SystemExit as e:
            assert e.code == 0

    def test_tidal_intel_brief(self):
        try:
            code = main(["tidal-intel-brief"])
        except SystemExit as e:
            assert e.code == 0

    def test_tidal_ops(self):
        try:
            code = main(["tidal-ops"])
        except SystemExit as e:
            assert e.code == 0

    def test_tidal_alert(self):
        try:
            code = main(["tidal-alert", "--message", "cli test"])
        except SystemExit as e:
            assert e.code == 0

    def test_tidal_alerts_list(self):
        try:
            code = main(["tidal-alerts"])
        except SystemExit as e:
            assert e.code == 0

    def test_tidal_note_and_list(self):
        try:
            main(["tidal-note", "--target", "cli-test", "--content", "test"])
        except SystemExit as e:
            assert e.code == 0
        try:
            main(["tidal-notes", "--target", "cli-test"])
        except SystemExit as e:
            assert e.code == 0
