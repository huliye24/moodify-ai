"""MHP-095 + MHP-112: Runtime Supervisor Tests.

Probe-level tests for run_supervised() and Build-level tests for the full supervisor.
"""

import time

from moodify_runtime.supervisor import run_supervised, SupervisedRun


def test_supervised_success():
    """Supervisor wraps a successful command and returns exit_code=0."""
    r = run_supervised(["echo", "hello"], timeout=5, max_retries=0)
    assert r.exit_code == 0
    assert not r.crashed
    assert not r.timed_out
    assert r.attempts == 1


def test_supervised_failure_no_retry():
    """Exit code != 0 with max_retries=0 should mark crashed."""
    r = run_supervised(["python3", "-c", "exit(1)"], timeout=5, max_retries=0)
    assert r.exit_code == 1
    assert r.crashed
    assert r.attempts == 1


def test_supervised_failure_with_retry():
    """With max_retries=2, should retry on failure."""
    r = run_supervised(["python3", "-c", "exit(1)"], timeout=5, max_retries=2, retry_delay=0.1)
    assert r.crashed
    assert r.attempts == 3  # 1 initial + 2 retries


def test_supervised_timeout():
    """sleep longer than timeout should trigger timeout detection."""
    r = run_supervised(["sleep", "2"], timeout=0.5, max_retries=0)
    assert r.timed_out
    assert r.crashed


def test_supervised_command_not_found():
    """Nonexistent command should crash."""
    r = run_supervised(["/nonexistent/cmd_xyz"], timeout=5, max_retries=0)
    assert r.crashed
    assert r.exit_code != 0 or r.error != ""


def test_supervised_retry_eventually_succeeds():
    """A command that fails once then succeeds should return success after retry."""
    # Use a temp file to track attempts
    import tempfile, pathlib
    tmp = pathlib.Path(tempfile.mkdtemp())
    state_file = tmp / "state.txt"
    script = tmp / "flaky.py"
    script.write_text(f"""
import sys
p = __import__('pathlib').Path('{state_file}')
count = 0
if p.exists():
    count = int(p.read_text())
p.write_text(str(count + 1))
if count < 1:
    sys.exit(1)
print("success")
sys.exit(0)
""")
    r = run_supervised(["python3", str(script)], timeout=5, max_retries=2, retry_delay=0.1)
    assert r.exit_code == 0
    assert not r.crashed
    assert r.attempts == 2  # failed once, succeeded on retry


def test_supervised_to_dict():
    """to_dict() should produce serializable output."""
    r = run_supervised(["echo", "test"], timeout=5, max_retries=0)
    d = r.to_dict()
    assert d["exit_code"] == 0
    assert not d["crashed"]
    assert "echo test" in d["command"]
