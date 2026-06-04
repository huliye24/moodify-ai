"""Tests for supervisor."""
from moodify_runtime.supervisor import SupervisedRun, run_supervised

class TestSupervisedRun:
    def test_default(self):
        sr = SupervisedRun(command=["echo", "test"])
        assert sr.exit_code == -1

class TestRunSupervised:
    def test_simple(self):
        result = run_supervised(["echo", "hello"], timeout=10, max_retries=1)
        assert result.exit_code == 0
    def test_failing(self):
        result = run_supervised(["false"], timeout=10, max_retries=1)
        assert result.exit_code != 0
    def test_nonexistent(self):
        result = run_supervised(["/nonexistent/cmd_xyz"], timeout=5, max_retries=1)
        assert not result.exit_code == 0 or result.crashed
