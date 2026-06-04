"""Tests for runtime_failures."""
from moodify_runtime.runtime_failures import (
    Severity, FailureRecord, classify_failure, should_retry, backoff_delay,
)

class TestFailureRecord:
    def test_default(self):
        fr = FailureRecord(failure_id="F1", task_id="T1")
        assert fr.failure_id == "F1"
    def test_retryable(self):
        fr = FailureRecord(failure_id="F2", task_id="T2", retryable=True)
        assert fr.retryable

class TestClassify:
    def test_ok(self):
        fr = classify_failure(0, "", attempt=0)
        assert fr.retryable
    def test_timeout_transient(self):
        fr = classify_failure(-1, "timed out", attempt=0)
        assert fr.retryable

class TestShouldRetry:
    def test_ok_no(self):
        fr = FailureRecord(failure_id="F3", task_id="T3", retryable=False)
        assert not should_retry(fr)
    def test_transient_yes(self):
        fr = FailureRecord(failure_id="F4", task_id="T4", retryable=True, severity=Severity.MEDIUM)
        assert should_retry(fr)

class TestBackoff:
    def test_increases(self):
        assert backoff_delay(2) >= backoff_delay(0)
    def test_capped(self):
        assert backoff_delay(100, max_delay=60.0) <= 60.0
